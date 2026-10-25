# Copyright (c) 2026 Daniel Ari Friedman
"""Build a portable, aggregate-only local workbench with inspectable source bindings."""

import base64
import hashlib
import json
import re
from collections import Counter
from importlib.resources import files
from pathlib import Path

from pydantic import TypeAdapter

from . import __version__
from .corpus import load_import
from .institutions import assess
from .manuscript import ManuscriptSpec, validate_manuscript
from .models import (
    Concordance,
    CorpusPin,
    Decision,
    FileReceipt,
    QuerySpec,
    ResearchError,
)
from .observations import reconcile_coverage
from .storage import digest, safe_path, write_new
from .workbench_models import CaseTrace, ReadingNote, Workbench
from .workbench_view import sections


def reading_notes(path: Path) -> tuple[ReadingNote, ...]:
    """Select display fields without embedding caches or modern full texts."""
    entries = TypeAdapter(list[dict[str, str]]).validate_json(path.read_bytes())
    return tuple(
        ReadingNote(
            source=entry["source"],
            reading_status=entry["reading_status"],
            locator=entry.get("locator"),
            url=entry.get("url"),
            sha256=entry.get("sha256"),
        )
        for entry in entries
    )


def build_workbench(
    root: Path,
    corpus: Path,
    concordance_file: Path,
    readings: str = "research/scholarship-reading-0.4.1.json",
) -> Workbench:
    """Reconcile the run against the verified independent projection before publication."""
    relative = (
        "research/corpus-pin.json",
        "research/queries.json",
        "research/cases.json",
        "research/manuscript-inputs.json",
        "docs/manuscript/states-change.md",
        readings,
    )
    paths = [safe_path(root, name) for name in relative]
    tracked = (*paths, concordance_file, corpus / "passages.sqlite")
    before = {path: digest(path) for path in tracked}
    pin = CorpusPin.model_validate_json(paths[0].read_bytes())
    queries = TypeAdapter(tuple[QuerySpec, ...]).validate_json(paths[1].read_bytes())
    records = TypeAdapter(tuple[Decision, ...]).validate_json(paths[2].read_bytes())
    if len({r.decision_id for r in records}) != len(records) or not records:
        raise ResearchError("report_cases", "Supply nonempty, unique synthetic decisions")
    spec = ManuscriptSpec.model_validate_json(paths[3].read_bytes())
    asset_paths = validate_manuscript(root, spec, paths[4].read_text())
    receipt, passages = load_import(corpus, pin)
    result = Concordance.model_validate_json(concordance_file.read_bytes())
    coverage = reconcile_coverage(result, passages, queries, pin)
    cases: list[CaseTrace] = []
    for record in records:
        original = assess(record)
        ablated = record.model_copy(
            update={
                "poetic_state_interpretation": None,
                "national_affiliations": (),
            }
        )
        cases.append(
            CaseTrace(
                record=record,
                assessment=original,
                poetic_label_ablation_invariant=assess(ablated) == original,
            )
        )
    consumed = (*paths, concordance_file, corpus / "passages.sqlite", *asset_paths.values())
    inputs = tuple(
        FileReceipt(
            path=path.absolute().relative_to(root.absolute()).as_posix(),
            size=path.stat().st_size,
            sha256=digest(path),
        )
        for path in consumed
    )
    if any(digest(path) != expected for path, expected in before.items()):
        raise ResearchError("report_source_changed", "An input changed during report preparation")
    package = files("blakean_federalism")
    producer_names = (
        "__init__.py",
        "report.py",
        "observations.py",
        "institutions.py",
        "corpus.py",
        "models.py",
        "manuscript.py",
        "storage.py",
        "resources/workbench.html",
        "resources/workbench.css",
        "resources/workbench.js",
        "workbench_view.py",
        "workbench_models.py",
        "resources/fonts/Vera.ttf",
        "resources/fonts/VeraBd.ttf",
        "resources/fonts/VeraIt.ttf",
        "resources/fonts/bitstream-vera-license.txt",
    )
    producer_sources = {
        name: hashlib.sha256(package.joinpath(name).read_bytes()).hexdigest()
        for name in producer_names
    }
    return Workbench(
        producer_version=__version__,
        corpus_pin=pin,
        source_units=receipt.passages,
        query_groups=queries,
        source_urls={a.asset_id: a.url for a in spec.assets if a.kind == "html"},
        query_count=len(queries),
        stored_occurrences=len(result.hits),
        coverage=coverage,
        cases=tuple(cases),
        quotations=spec.quotations,
        images=tuple(a for a in spec.assets if a.kind == "image"),
        reading=reading_notes(paths[5]),
        inputs=inputs,
        producer_sources=producer_sources,
    )


def csp_hash(value: str) -> str:
    return base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()


def stylesheet() -> str:
    directory = files("blakean_federalism").joinpath("resources")
    css = directory.joinpath("workbench.css").read_text(encoding="utf-8")
    for marker, name in (
        ("@@FONT_REGULAR@@", "Vera.ttf"),
        ("@@FONT_BOLD@@", "VeraBd.ttf"),
        ("@@FONT_ITALIC@@", "VeraIt.ttf"),
    ):
        css = css.replace(
            marker, base64.b64encode(directory.joinpath("fonts", name).read_bytes()).decode()
        )
    return css


def html_document(report: Workbench) -> str:
    """Inline package-owned resources, escape data for script context, forbid network fetches."""
    directory = files("blakean_federalism").joinpath("resources")
    template = directory.joinpath("workbench.html").read_text(encoding="utf-8")
    css = stylesheet()
    script = directory.joinpath("workbench.js").read_text(encoding="utf-8")
    payload = (
        report.model_dump_json()
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("&", r"\u0026")
    )
    policy = f"""default-src 'none'; base-uri 'none'; form-action 'none'; font-src data:;
style-src 'sha256-{csp_hash(css)}';
script-src 'sha256-{csp_hash(script)}' 'sha256-{csp_hash(payload)}'"""

    values = sections(report) | {
        "@@POLICY@@": policy,
        "@@CSS@@": css,
        "@@SCRIPT@@": script,
        "@@DATA@@": payload,
    }
    markers = re.findall(r"@@[A-Z_]+@@", template)
    if Counter(markers) != Counter(values.keys()):
        raise ResearchError("report_template", "Template fields must be complete and unique")
    return re.sub(r"@@[A-Z_]+@@", lambda match: values[match.group()], template)


def publish_workbench(report: Workbench, destination: Path) -> Path:
    """Reserve a new ignored output slot; never replace earlier reports."""
    root = Path.cwd().absolute()
    if (
        any(p.is_symlink() for p in (destination, *destination.parents))
        or ".." in destination.parts
        or not destination.absolute().is_relative_to(root / "analysis_output")
    ):
        raise ResearchError("report_output", "Use a new regular directory under analysis_output")
    html = html_document(report)
    data = report.model_dump_json(indent=2) + "\n"
    destination.mkdir(parents=True, exist_ok=False)
    target = destination / "research-workbench.html"
    write_new(target, html)
    write_new(destination / "workbench-data.json", data)
    manifest = {
        "producer_version": report.producer_version,
        "outputs": {
            name: digest(destination / name)
            for name in (
                "research-workbench.html",
                "workbench-data.json",
            )
        },
        "input_bindings": [entry.model_dump(mode="json") for entry in report.inputs],
        "browser_review": "Not implied by generation; recorded separately",
    }
    write_new(destination / "report-receipt.json", json.dumps(manifest, indent=2) + "\n")
    return target
