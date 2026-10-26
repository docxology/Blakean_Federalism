# Copyright (c) 2026 Daniel Ari Friedman
"""Real imported source, Unicode tables and private-output custody controls."""

import json
import os
import re
from contextlib import contextmanager
from itertools import pairwise
from pathlib import Path

import pytest

from blakean_federalism.corpus import import_corpus
from blakean_federalism.models import ResearchError
from blakean_federalism.search_workspace import (
    _csp_hash,
    _json_script,
    build_search_workspace,
    unicode_search_tables,
)
from blakean_federalism.storage import digest


@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def test_unicode_tables_match_python_boundaries_and_expansions():
    folding, ranges = unicode_search_tables()
    assert folding["ß"] == "ss"
    assert folding["İ"] == "i\u0307"
    assert folding["\u03a3"] == "\u03c3"
    assert "😀" not in folding
    assert folding["𐐀"] == "𐐨"
    assert all(left[1] + 1 < right[0] for left, right in pairwise(ranges))
    for value in ("A", "_", "é", "Ⅷ", "²", "𐐀", "𐐨", "😀", "\u0307", " ", "-"):
        included = any(start <= ord(value) <= end for start, end in ranges)
        assert included == (value.isalnum() or value == "_")


def test_script_serialization_is_inert_and_lossless():
    unsafe = {"text": '</script><script>alert("x")</script>\u2028\u2029 @@SCRIPT@@'}
    encoded = _json_script(unsafe)
    assert "</script>" not in encoded
    assert "\u2028" not in encoded
    assert "\u2029" not in encoded
    assert json.loads(encoded) == unsafe
    assert len(_csp_hash("source")) == 44
    assert _csp_hash("source") != _csp_hash("changed")


def test_workspace_has_complete_bound_fulltexts_and_no_runtime_network(captured):
    source, _, pin, imported, payloads = captured
    import_corpus(source, imported, pin)
    with working_directory(imported.parent):
        output = Path("analysis_output/search")
        index = build_search_workspace(imported, pin, output)
        html = index.read_text()
        matched = re.search(
            r'<script id="search-data" type="application/json">(.*?)</script>', html, re.DOTALL
        )
        assert matched is not None
        payload = json.loads(matched[1])
        assert [unit["text"] for unit in payload["units"]] == [p["text"] for p in payloads]
        assert payload["corpus_pin"] == pin.model_dump(mode="json")
        assert payload["units"][0]["text_sha256"]
        assert "fetch(" not in html
        assert "XMLHttpRequest" not in html
        assert "connect-src 'none'" in html
        assert "window.blakeanSearch=Object.freeze({run})" in html
        assert "innerHTML" not in html
        assert "javascript:" not in html
        assert "@@STYLE@@" not in html
        assert str(imported) not in html
        receipt = json.loads((output / "search-manifest.json").read_text())
        assert receipt["source_units"] == 2
        assert receipt["index_sha256"] == pin.index_sha256
        assert receipt["outputs"][0]["sha256"] == digest(index)
        assert receipt["outputs"][0]["size"] == index.stat().st_size
        with pytest.raises(ResearchError, match="occupied_output"):
            build_search_workspace(imported, pin, output)


def test_workspace_refuses_public_paths_traversal_and_symlink(captured):
    source, _, pin, imported, _ = captured
    import_corpus(source, imported, pin)
    with working_directory(imported.parent):
        for destination in (Path("docs/search"), Path("analysis_output/../docs/search")):
            with pytest.raises(ResearchError, match="private_output_required"):
                build_search_workspace(imported, pin, destination)
        (Path.cwd() / "analysis_output").mkdir()
        (Path.cwd() / "link").symlink_to(Path.cwd() / "analysis_output", target_is_directory=True)
        with pytest.raises(ResearchError, match="symlink_output"):
            build_search_workspace(imported, pin, Path("link/search"))


def test_workspace_rejects_corrupted_projection_before_publication(captured):
    source, _, pin, imported, _ = captured
    import_corpus(source, imported, pin)
    with (imported / "passages.sqlite").open("ab") as stream:
        stream.write(b"corrupted")
    with working_directory(imported.parent), pytest.raises(ResearchError, match="import_checksum"):
        build_search_workspace(imported, pin, Path("analysis_output/search"))
    assert not (imported.parent / "analysis_output/search").exists()
