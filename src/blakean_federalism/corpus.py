# Copyright (c) 2026 Daniel Ari Friedman
"""Import and search an independent, pinned local projection without changing Blake."""

import hashlib
import json
import re
import shutil
import sqlite3
import tempfile
from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path
from typing import Final

from pydantic import TypeAdapter

from .models import (
    Concordance,
    CorpusPin,
    CountRow,
    Hit,
    ImportReceipt,
    Passage,
    Plane,
    Projection,
    QuerySpec,
    ResearchError,
    Role,
)
from .storage import digest, safe_path, verify_file

ROWS: Final = TypeAdapter(tuple[tuple[str, str, str], ...])


def read_passages(index: Path) -> tuple[Passage, ...]:
    """Parse all SQLite payloads and independently verify each stored text digest."""
    result: list[Passage] = []
    with closing(sqlite3.connect(index.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        if conn.execute("PRAGMA quick_check").fetchone() != ("ok",):
            raise ResearchError("sqlite_integrity", str(index))
        rows = ROWS.validate_python(
            conn.execute(
                "SELECT id,payload,sha256 FROM passages ORDER BY id",
            ).fetchall()
        )
        for identity, payload, text_sha in rows:
            passage = Passage.model_validate_json(payload)
            actual = hashlib.sha256(passage.text.encode()).hexdigest()
            if identity != passage.passage_id or text_sha != actual:
                raise ResearchError("passage_binding", identity)
            result.append(passage)
    return tuple(result)


def import_corpus(data_root: Path, destination: Path, pin: CorpusPin) -> ImportReceipt:
    """Verify every consumed input, then copy only the text projection into a new slot."""
    upstream = data_root.resolve()
    target = destination.resolve()
    if target.is_relative_to(upstream) or upstream.is_relative_to(target):
        raise ResearchError("overlapping_roots", str(target))
    if destination.exists():
        raise ResearchError("occupied_output", str(destination))
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ResearchError("symlink_output", str(destination))
    capture = safe_path(data_root, "recovery/manifest.json")
    metadata = safe_path(data_root, pin.projection_relative_path + "/search-manifest.json")
    if digest(capture) != pin.captured_manifest_sha256:
        raise ResearchError("capture_pin", str(capture))
    if digest(metadata) != pin.projection_manifest_sha256:
        raise ResearchError("projection_pin", str(metadata))
    projection = Projection.model_validate_json(metadata.read_bytes())
    if projection.captured_manifest_sha256 != pin.captured_manifest_sha256:
        raise ResearchError("source_binding", str(metadata))
    if projection.index.sha256 != pin.index_sha256 or projection.index.path != "passages.sqlite":
        raise ResearchError("index_pin", str(metadata))
    source = verify_file(
        metadata.parent,
        projection.index.path,
        projection.index.size,
        pin.index_sha256,
    )
    paths = [
        verify_file(data_root / "recovery", r.path, r.size, r.sha256) for r in projection.inputs
    ]
    passages = read_passages(source)
    identities = tuple(p.passage_id for p in passages)
    if (
        len(passages) != projection.passages
        or len(set(projection.passage_ids)) != projection.passages
        or set(identities) != set(projection.passage_ids)
        or dict(Counter(p.source_plane for p in passages)) != projection.passages_by_plane
        or dict(Counter(p.text_role for p in passages)) != projection.passages_by_role
    ):
        raise ResearchError("projection_membership", str(metadata))
    receipt = ImportReceipt(
        corpus_pin=pin,
        passages=len(passages),
        consumed_inputs_verified=len(paths),
        passages_by_plane=projection.passages_by_plane,
        passages_by_role=projection.passages_by_role,
        source_capture_path=str(data_root.absolute()),
        independence="copied bytes; no upstream writes or linked payloads",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="import-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        _ = shutil.copyfile(source, stage / "passages.sqlite")
        _ = shutil.copyfile(metadata, stage / "search-manifest.json")
        _ = shutil.copyfile(capture, stage / "capture-manifest.json")
        _ = (stage / "import-receipt.json").write_text(receipt.model_dump_json(indent=2) + "\n")
        if digest(stage / "passages.sqlite") != pin.index_sha256:
            raise ResearchError("copy_integrity", str(stage))
        for r in projection.inputs:
            _ = verify_file(data_root / "recovery", r.path, r.size, r.sha256)
        if (
            digest(capture) != pin.captured_manifest_sha256
            or digest(metadata) != pin.projection_manifest_sha256
            or digest(source) != pin.index_sha256
        ):
            raise ResearchError("source_changed", str(data_root))
        if destination.exists():
            raise ResearchError("occupied_output", str(destination))
        _ = stage.rename(destination)
    return receipt


def load_import(
    directory: Path, expected_pin: CorpusPin
) -> tuple[ImportReceipt, tuple[Passage, ...]]:
    receipt = ImportReceipt.model_validate_json(
        safe_path(directory, "import-receipt.json").read_bytes(),
    )
    pin = receipt.corpus_pin
    if pin != expected_pin:
        raise ResearchError("untrusted_import_pin", str(directory))
    for relative, expected in (
        ("passages.sqlite", pin.index_sha256),
        ("search-manifest.json", pin.projection_manifest_sha256),
        ("capture-manifest.json", pin.captured_manifest_sha256),
    ):
        if digest(safe_path(directory, relative)) != expected:
            raise ResearchError("import_checksum", relative)
    passages = read_passages(directory / "passages.sqlite")
    if len(passages) != receipt.passages:
        raise ResearchError("import_membership", str(directory))
    return receipt, passages


def concordance(
    directory: Path,
    queries: tuple[QuerySpec, ...],
    expected_pin: CorpusPin,
) -> Concordance:
    """Retain exact case-insensitive word spans in each original source plane and role."""
    if not queries or len({q.query_id for q in queries}) != len(queries):
        raise ResearchError("query_membership", "Provide nonempty, unique query identifiers")
    receipt, passages = load_import(directory, expected_pin)
    text_hashes = {p.passage_id: hashlib.sha256(p.text.encode()).hexdigest() for p in passages}
    hits: list[Hit] = []
    rows: list[CountRow] = []
    for query in queries:
        if any(not term.strip() for term in query.variants):
            raise ResearchError("empty_variant", query.query_id)
        expression = (
            r"(?<!\w)(?:"
            + "|".join(
                re.escape(term) for term in sorted(set(query.variants), key=len, reverse=True)
            )
            + r")(?!\w)"
        )
        pattern = re.compile(expression, re.IGNORECASE)
        totals: Counter[tuple[Plane, Role]] = Counter()
        documents: defaultdict[tuple[Plane, Role], set[str]] = defaultdict(set)
        for passage in passages:
            for match in pattern.finditer(passage.text):
                key = (passage.source_plane, passage.text_role)
                totals[key] += 1
                documents[key].add(passage.passage_id)
                hits.append(
                    Hit(
                        query_id=query.query_id,
                        passage_id=passage.passage_id,
                        work_id=passage.work_id,
                        title=passage.title,
                        edition_id=passage.edition_id,
                        locator=passage.locator,
                        source_url=passage.source_url,
                        plane=passage.source_plane,
                        role=passage.text_role,
                        text_sha256=text_hashes[passage.passage_id],
                        start=match.start(),
                        end=match.end(),
                        expression=match.group(),
                        context=passage.text[max(0, match.start() - 100) : match.end() + 100],
                    )
                )
        for plane in Plane:
            for role in Role:
                key = (plane, role)
                rows.append(
                    CountRow(
                        query_id=query.query_id,
                        plane=plane,
                        role=role,
                        occurrences=totals[key],
                        matched_source_documents=len(documents[key]),
                    )
                )
    query_bytes = json.dumps([q.model_dump(mode="json") for q in queries], sort_keys=True).encode()
    return Concordance(
        pin=receipt.corpus_pin,
        query_sha256=hashlib.sha256(query_bytes).hexdigest(),
        scanned_source_documents=len(passages),
        rows=tuple(rows),
        hits=tuple(hits),
    )
