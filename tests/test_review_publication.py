# Copyright (c) 2026 Daniel Ari Friedman
"""Real approved-tool execution and publication custody guards."""

import shutil
import subprocess
from pathlib import Path

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.review_publication import prepare_review_figures
from blakean_federalism.storage import digest

ROOT = Path(__file__).parents[1]


@pytest.fixture
def inputs(tmp_path):
    for name in (
        "research/institutional-review-cases.json",
        "research/cases.json",
        "tools/audit_institutional_review.py",
    ):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    stage = tmp_path / "analysis_output" / "publication"
    (stage / "output/figures").mkdir(parents=True)
    return tmp_path, stage


def test_real_domain_figures_are_bound_and_copied(inputs):
    root, stage = inputs
    before = digest(root / "research/cases.json")
    result = prepare_review_figures(root, stage)
    assert set(result) == {"institutional-review", "review-continuity"}
    for name in result:
        for suffix in (".png", ".pdf"):
            source = stage / "review-audit/figures" / (name + suffix)
            target = stage / "output/figures" / (name + suffix)
            assert digest(source) == digest(target)
            assert source.stat().st_ino != target.stat().st_ino
    assert digest(root / "research/cases.json") == before
    assert (stage / "review-audit/review-receipt.json").is_file()


def test_bad_baseline_retains_failure_log_without_figure_copy(inputs):
    root, stage = inputs
    baseline = root / "research/cases.json"
    baseline.write_text(baseline.read_text() + "\n")
    with pytest.raises(subprocess.CalledProcessError):
        prepare_review_figures(root, stage)
    assert "baseline_hash_mismatch" in (stage / "review-audit.log").read_text()
    assert not tuple((stage / "output/figures").iterdir())


def test_source_mutation_after_real_audit_blocks_copy(inputs):
    root, stage = inputs
    tool = root / "tools/audit_institutional_review.py"
    source = root / "research/cases.json"
    text = tool.read_text()
    mutation = (
        f"\nimport atexit\natexit.register(lambda: Path({str(source)!r}).write_bytes(b'changed'))\n"
    )
    tool.write_text(
        text.replace('if __name__ == "__main__":', mutation + 'if __name__ == "__main__":')
    )
    with pytest.raises(ResearchError, match="review_source_changed"):
        prepare_review_figures(root, stage)
    assert not tuple((stage / "output/figures").iterdir())
