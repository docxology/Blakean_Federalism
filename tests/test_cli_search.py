# Copyright (c) 2026 Daniel Ari Friedman
"""Search CLI uses a real independently imported SQLite corpus."""

import json
from contextlib import chdir

from typer.testing import CliRunner

from blakean_federalism.cli import app
from blakean_federalism.corpus import import_corpus


def test_search_cli_counts_caps_and_scope(captured):
    source, _, pin, _, _ = captured
    root = source.parent
    (root / "research").mkdir()
    (root / "research/corpus-pin.json").write_text(pin.model_dump_json())
    import_corpus(source, root / "local_data/corpus/blake-v0.2.0-qualified", pin)
    with chdir(root):
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "search-corpus",
                "--term",
                "state",
                "--term",
                "states",
                "--limit",
                "1",
                "--output",
                "analysis_output/search.json",
            ],
        )
        assert result.exit_code == 0, result.output
        data = json.loads((root / "analysis_output/search.json").read_text())
        assert data["total_occurrences"] == 3
        assert data["returned_hits"] == 1
        assert data["truncated"]
        assert data["corpus_pin"] == json.loads(pin.model_dump_json())
        all_sources = runner.invoke(
            app,
            [
                "search-corpus",
                "--term",
                "state",
                "--all-sources",
                "--output",
                "analysis_output/all.json",
            ],
        )
        assert all_sources.exit_code == 0, all_sources.output
        assert json.loads((root / "analysis_output/all.json").read_text())["total_occurrences"] == 2
        repeated = runner.invoke(
            app, ["search-corpus", "--term", "state", "--output", "analysis_output/search.json"]
        )
        assert repeated.exit_code != 0
        assert json.loads((root / "analysis_output/search.json").read_text()) == data
        contradictory = runner.invoke(
            app,
            [
                "search-corpus",
                "--term",
                "state",
                "--role",
                "editorial",
                "--all-sources",
                "--output",
                "analysis_output/bad.json",
            ],
        )
        assert contradictory.exit_code != 0
        assert not (root / "analysis_output/bad.json").exists()


def test_search_cli_private_output_boundary(tmp_path):
    with chdir(tmp_path):
        for command in (["search-corpus", "--term", "state"], ["build-search-workspace"]):
            result = CliRunner().invoke(app, [*command, "--output", "research/leak"])
            assert result.exit_code != 0
            assert not (tmp_path / "research/leak").exists()


def test_search_workspace_cli(captured):
    source, _, pin, _, _ = captured
    root = source.parent
    (root / "research").mkdir()
    (root / "research/corpus-pin.json").write_text(pin.model_dump_json())
    import_corpus(source, root / "local_data/corpus/blake-v0.2.0-qualified", pin)
    with chdir(root):
        result = CliRunner().invoke(
            app, ["build-search-workspace", "--output", "analysis_output/search"]
        )
    assert result.exit_code == 0, result.output
    assert (root / "analysis_output/search/index.html").is_file()
