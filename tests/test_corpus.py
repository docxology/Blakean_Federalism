# Copyright (c) 2026 Daniel Ari Friedman
"""Real-file controls for custody, role separation and bounded lexical retrieval."""

import json
import sqlite3
from contextlib import closing

import pytest

from blakean_federalism.corpus import concordance, import_corpus, load_import, read_passages
from blakean_federalism.models import FileReceipt, Passage, QuerySpec, ResearchError
from blakean_federalism.storage import copy_new, digest, publish_projection, safe_path, write_new


def test_import_is_independent_and_preserves_source(captured):
    source, projection, pin, dest, _ = captured
    before = digest(projection / "passages.sqlite")
    # When copying, then bytes agree while storage is independent and source unchanged.
    receipt = import_corpus(source, dest, pin)
    assert receipt.passages == 2
    assert digest(dest / "passages.sqlite") == before == digest(projection / "passages.sqlite")
    assert (dest / "passages.sqlite").stat().st_ino != (
        projection / "passages.sqlite"
    ).stat().st_ino


@pytest.mark.parametrize("target", ["capture", "projection", "index", "input"])
def test_changed_input_cannot_be_imported(captured, target):
    source, projection, pin, dest, _ = captured
    targets = {
        "capture": source / "recovery/manifest.json",
        "projection": projection / "search-manifest.json",
        "index": projection / "passages.sqlite",
        "input": source / "recovery/input.txt",
    }
    with targets[target].open("ab") as stream:
        stream.write(b"changed")
    # When one input changes, then refuse without publishing a destination.
    with pytest.raises(ResearchError):
        import_corpus(source, dest, pin)
    assert not dest.exists()


def test_symlink_input_is_refused(captured):
    source, _, pin, dest, _ = captured
    old = source / "recovery/input.txt"
    saved = source / "recovery/saved.txt"
    old.rename(saved)
    old.symlink_to(saved)
    # When importing a symlinked input, then no target is published.
    with pytest.raises(ResearchError, match="symlink"):
        import_corpus(source, dest, pin)


def test_source_directory_symlink_is_refused(captured):
    source, _, pin, dest, _ = captured
    alias = source.parent / "alias"
    alias.symlink_to(source, target_is_directory=True)
    # When the declared source root is a link, then refuse.
    with pytest.raises(ResearchError, match="symlink"):
        import_corpus(alias, dest, pin)


def test_import_cannot_overwrite(captured):
    source, _, pin, dest, _ = captured
    dest.mkdir()
    # When a destination is occupied, then preserve it.
    with pytest.raises(ResearchError, match="occupied"):
        import_corpus(source, dest, pin)


def test_overlapping_destination_is_refused(captured):
    source, _, pin, _, _ = captured
    # When the destination enters upstream custody, then refuse.
    with pytest.raises(ResearchError, match="overlapping"):
        import_corpus(source, source / "derived", pin)


def test_corrupt_import_fails_on_open(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    with (dest / "passages.sqlite").open("ab") as stream:
        stream.write(b"damage")
    # When copied bytes change, then readers refuse.
    with pytest.raises(ResearchError, match="import_checksum"):
        load_import(dest, pin)


def test_altered_import_receipt_pin_is_untrusted(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    data = json.loads((dest / "import-receipt.json").read_text())
    data["corpus_pin"]["upstream_commit"] = "different"
    (dest / "import-receipt.json").write_text(json.dumps(data))
    # When a receipt claims new provenance, then the external pin wins.
    with pytest.raises(ResearchError, match="untrusted_import_pin"):
        load_import(dest, pin)


def test_concordance_preserves_roles_spans_and_whole_words(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    query = QuerySpec(query_id="states", variants=("state", "states"), note="Explicit forms")
    # When searching, then four known tokens exclude the substring in statement.
    result = concordance(dest, (query,), pin)
    assert len(result.hits) == 4
    assert [(r.role.value, r.occurrences) for r in result.rows if r.occurrences] == [
        ("primary", 3),
        ("editorial", 1),
    ]
    _, passages = load_import(dest, pin)
    texts = {p.passage_id: p.text for p in passages}
    assert all(texts[h.passage_id][h.start : h.end] == h.expression for h in result.hits)


def test_literal_metacharacters_are_not_regex(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    # When a term includes a dot, then only the literal is returned.
    result = concordance(
        dest, (QuerySpec(query_id="literal", variants=("a.b",), note="Literal"),), pin
    )
    assert [h.expression for h in result.hits] == ["a.b"]


@pytest.mark.parametrize(
    "queries",
    [
        (),
        (QuerySpec(query_id="x", variants=("state",), note="a"),) * 2,
        (QuerySpec(query_id="x", variants=(" ",), note="a"),),
    ],
)
def test_invalid_query_sets_are_refused(captured, queries):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    # When queries are empty, duplicated or blank, then fail.
    with pytest.raises(ResearchError):
        concordance(dest, queries, pin)


def test_negative_query_has_explicit_zero_rows(captured):
    source, _, pin, dest, _ = captured
    import_corpus(source, dest, pin)
    # When an absent token is searched, then every cell is explicitly zero.
    result = concordance(
        dest, (QuerySpec(query_id="none", variants=("zzzxqv",), note="Control"),), pin
    )
    assert not result.hits
    assert len(result.rows) == 9
    assert all(row.occurrences == row.matched_source_documents == 0 for row in result.rows)


def test_raw_xml_cannot_be_promoted_to_primary(captured):
    payload = captured[4][0] | {"source_plane": "xml"}
    # When raw XML claims primary status, then refuse.
    with pytest.raises(ResearchError, match="primary_plane"):
        Passage.model_validate(payload)


def test_passage_hash_is_checked_independently(captured):
    projection = captured[1]
    with closing(sqlite3.connect(projection / "passages.sqlite")) as db, db:
        db.execute("UPDATE passages SET sha256=?", ("0" * 64,))
    # When a text hash is false, then reject even in an otherwise valid database.
    with pytest.raises(ResearchError, match="passage_binding"):
        read_passages(projection / "passages.sqlite")


@pytest.mark.parametrize("relative", ["../escape", "/absolute", "folder\\escape"])
def test_traversal_paths_are_refused(tmp_path, relative):
    # When the boundary receives traversal, then refuse.
    with pytest.raises(ResearchError, match="unsafe"):
        safe_path(tmp_path, relative)


def test_write_new_preserves_prior_bytes(tmp_path):
    path = tmp_path / "result"
    path.write_text("original")
    # When another run targets the same output, then preserve the original.
    with pytest.raises(ResearchError, match="occupied"):
        write_new(path, "new")
    assert path.read_text() == "original"


def test_overlap_check_normalizes_parent_segments(captured):
    source, _, pin, _, _ = captured
    (source.parent / "outer").mkdir()
    destination = source.parent / "outer" / ".." / "source" / "derived"
    with pytest.raises(ResearchError, match="overlapping"):
        import_corpus(source, destination, pin)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("captured_manifest_sha256", "0" * 64, "source_binding"),
        ("passage_ids", ["p1", "p1"], "projection_membership"),
    ],
)
def test_rebound_metadata_still_must_reconcile(captured, field, value, code):
    source, projection, pin, dest, _ = captured
    path = projection / "search-manifest.json"
    metadata = json.loads(path.read_text())
    metadata[field] = value
    path.write_text(json.dumps(metadata))
    rebound = pin.model_copy(update={"projection_manifest_sha256": digest(path)})
    with pytest.raises(ResearchError, match=code):
        import_corpus(source, dest, rebound)


def test_import_refuses_a_dangling_destination_link(captured):
    source, _, pin, dest, _ = captured
    dest.symlink_to(dest.parent / "absent")
    with pytest.raises(ResearchError, match="symlink_output"):
        import_corpus(source, dest, pin)


def test_exclusive_copy_preserves_existing_file(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"new bytes")
    destination = tmp_path / "destination"
    destination.write_bytes(b"prior owner")
    with pytest.raises(ResearchError, match="occupied_output"):
        copy_new(source, destination)
    assert destination.read_bytes() == b"prior owner"


def test_exclusive_copy_refuses_dangling_link(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"new bytes")
    destination = tmp_path / "destination"
    destination.symlink_to(tmp_path / "absent")
    with pytest.raises(ResearchError, match="occupied_output"):
        copy_new(source, destination)
    assert destination.is_symlink()


def test_publication_cannot_replace_a_concurrently_created_empty_directory(tmp_path):
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / "payload").write_bytes(b"data")
    receipt = FileReceipt(path="payload", size=4, sha256=digest(stage / "payload"))
    target = tmp_path / "other-owner"
    target.mkdir()
    original_inode = target.stat().st_ino
    with pytest.raises(ResearchError, match="occupied_output"):
        publish_projection(stage, target, (receipt,), "{}")
    assert target.stat().st_ino == original_inode
    assert list(target.iterdir()) == []
