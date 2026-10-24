# Copyright (c) 2026 Daniel Ari Friedman
import hashlib
import json
import sqlite3

import pytest
from PIL import Image

from blakean_federalism.manuscript import ManuscriptSpec
from blakean_federalism.models import CorpusPin
from blakean_federalism.storage import digest


@pytest.fixture
def captured(tmp_path):
    # Given real source bytes and SQLite rows with known authorship boundaries.
    source = tmp_path / "source"
    recovery = source / "recovery"
    projection = source / "search/pinned"
    recovery.mkdir(parents=True)
    projection.mkdir(parents=True)
    (recovery / "manifest.json").write_text('{"test_fixture":true}')
    (recovery / "input.txt").write_text("Retained source bytes")
    common = dict(
        work_id="test",
        title="Test",
        edition_id="ed",
        edition="Test",
        copy_id=None,
        locator="plate 32",
        locator_kind="plate",
        source_url="https://example.test/source",
        rights="Test only",
        source_sha256=None,
    )
    payloads = [
        common
        | dict(
            passage_id="p1",
            author_id="william-blake-1757-1827",
            text_role="primary",
            source_plane="reading",
            text="States change. A statement is not a state. Nations are not states.",
        ),
        common
        | dict(
            passage_id="p2",
            author_id="mixed-edition",
            text_role="editorial",
            source_plane="erdman",
            text="State and nation. a.b and axb.",
        ),
    ]
    with sqlite3.connect(projection / "passages.sqlite") as db:
        db.execute("CREATE TABLE passages (id TEXT PRIMARY KEY,payload TEXT,sha256 TEXT)")
        db.executemany(
            "INSERT INTO passages VALUES(?,?,?)",
            [
                (p["passage_id"], json.dumps(p), hashlib.sha256(p["text"].encode()).hexdigest())
                for p in payloads
            ],
        )
    m = dict(
        captured_manifest_sha256=digest(recovery / "manifest.json"),
        index=dict(
            path="passages.sqlite",
            size=(projection / "passages.sqlite").stat().st_size,
            sha256=digest(projection / "passages.sqlite"),
        ),
        inputs=[
            dict(
                path="input.txt",
                size=(recovery / "input.txt").stat().st_size,
                sha256=digest(recovery / "input.txt"),
            )
        ],
        passages=2,
        passage_ids=["p1", "p2"],
        passages_by_plane={"reading": 1, "erdman": 1},
        passages_by_role={"primary": 1, "editorial": 1},
    )
    (projection / "search-manifest.json").write_text(json.dumps(m))
    pin = CorpusPin(
        upstream_commit="test-fixture",
        captured_manifest_sha256=m["captured_manifest_sha256"],
        projection_manifest_sha256=digest(projection / "search-manifest.json"),
        projection_relative_path="search/pinned",
        index_sha256=m["index"]["sha256"],
        unresolved_images=0,
        scope_note="Synthetic test only",
    )
    return source, projection, pin, tmp_path / "imported", payloads


@pytest.fixture
def manuscript(tmp_path):
    assets = []
    for name in ("M32", "J52", "J54", "J73"):
        path = tmp_path / (name + ".png")
        Image.new("RGB", (20, 30), "white").save(path)
        assets.append(
            dict(
                asset_id=name,
                path=path.name,
                url="https://example.org/image",
                sha256=digest(path),
                size=path.stat().st_size,
                kind="image",
                caption="Synthetic test image; not a Blake reproduction",
                rights_basis="Test fixture",
                credit="Test",
                rights_url="https://example.org",
            )
        )
    html = tmp_path / "source.html"
    html.write_text(
        '<br><a name="M1.1;E1"></a><font size="-2">locator</font>'
        "Persons &amp; states<sup>editorial note</sup><br>"
    )
    assets.append(
        dict(
            asset_id="text",
            path=html.name,
            url="https://example.org/text",
            sha256=digest(html),
            size=html.stat().st_size,
            kind="html",
        )
    )
    quotes = [
        dict(
            quote_id=q,
            asset_id="text",
            locator="Synthetic M1.1; E1",
            segments=[dict(anchor="M1.1;E1", occurrence=0, text="Persons & states")],
            context="Synthetic test only",
        )
        for q in ("Q03", "Q05", "Q07", "Q08")
    ]
    spec = ManuscriptSpec.model_validate(
        dict(
            version="0.2.0",
            assets=assets,
            quotations=quotes,
            fronts=["composition", "warrants", "authority", "countermodels"],
        )
    )
    for folder in ("research", "docs/manuscript", "src/blakean_federalism"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "research/manuscript-inputs.json").write_text(spec.model_dump_json())
    (tmp_path / "docs/manuscript/states-change.md").write_text(
        "# Synthetic article\n\n"
        + "> Persons & states\n\n" * 4
        + "A **real** PDF with *italics* and [source](https://example.org).\n"
    )
    (tmp_path / "docs/manuscript/references-and-rights.md").write_text(
        "## Sources\n\nSynthetic rights.\n"
    )
    (tmp_path / "src/blakean_federalism/manuscript.py").write_text("# synthetic receipt binding\n")
    return tmp_path, spec
