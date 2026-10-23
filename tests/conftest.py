# Copyright (c) 2026 Daniel Ari Friedman
import hashlib
import json
import sqlite3

import pytest

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
