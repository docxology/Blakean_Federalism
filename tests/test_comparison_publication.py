# Copyright (c) 2026 Daniel Ari Friedman
"""Real domain producer integration without final native manuscript rendering."""

import json
import shutil
from pathlib import Path

import pytest

from blakean_federalism.comparison_publication import prepare_domain_figures
from blakean_federalism.manuscript import ManuscriptSpec, validate_manuscript
from blakean_federalism.publication_contract import manuscript_contract
from blakean_federalism.review_comparison_run import ComparisonReceipt
from blakean_federalism.storage import digest

ROOT = Path(__file__).parents[1]


@pytest.fixture
def source_stage(tmp_path):
    for name in ("research/cases.json", "research/institutional-review-cases.json"):
        target = tmp_path / name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    stage = tmp_path / "analysis_output" / "publication"
    (stage / "output/figures").mkdir(parents=True)
    return tmp_path, stage


def test_real_publication_adapter_copies_bound_figures_and_generated_captions(source_stage):
    # Given a source stage, when preparing selected domain figures, retain their complete run.
    root, stage = source_stage
    result = prepare_domain_figures(
        root, stage, ("fig:review-requirements", "fig:review-comparability")
    )
    receipt = ComparisonReceipt.model_validate_json(
        (stage / "review-comparison/comparison-receipt.json").read_bytes()
    )
    assert len(result.figures) == 2
    assert set(result.captions) == {"REVIEW_REQUIREMENTS_CAPTION", "REVIEW_COMPARISON_CAPTION"}
    assert all(
        name in result.captions["REVIEW_REQUIREMENTS_CAPTION"]
        for name in ("H01", "H05", "H12", "H13")
    )
    for item in receipt.outputs:
        if item.path.startswith("figures/"):
            source = stage / "review-comparison" / item.path
            target = stage / "output" / item.path
            assert digest(source) == digest(target) == item.sha256
            assert source.stat().st_ino != target.stat().st_ino


def test_manuscript_without_domain_labels_runs_no_domain_producer(source_stage):
    # Given no domain figure declarations, when preparing, do not invent an unused analysis.
    root, stage = source_stage
    result = prepare_domain_figures(root, stage, ())
    assert result.figures == {}
    assert result.captions == {}
    assert not (stage / "review-comparison").exists()


def test_current_source_contract_and_existing_quotation_selection_remain_valid():
    # Given the integrated article, when validated, native references and old quotations still bind.
    article = (ROOT / "docs/manuscript/states-change.md").read_text()
    appendix = (ROOT / "docs/manuscript/references-and-rights.md").read_text()
    notation = (ROOT / "docs/manuscript/notation.md").read_text()
    bibliography = (ROOT / "docs/manuscript/references.bib").read_text()
    spec = ManuscriptSpec.model_validate_json(
        (ROOT / "research/manuscript-inputs.json").read_bytes()
    )
    contract = manuscript_contract(notation + "\n" + article + "\n" + appendix, bibliography)
    assets = validate_manuscript(ROOT, spec, article + "\n" + appendix)
    assert {"fig:review-requirements", "fig:review-comparability"} <= set(contract.figure_labels)
    assert "def:review-requirements" in contract.formalism_numbers
    assert "prop:review-order" in contract.formalism_numbers
    assert "eq:review-requirements" in contract.equation_labels
    assert len(spec.quotations) == 40
    assert assets


def test_primary_rereading_records_retain_actual_source_hashes():
    # Given the new selected-reading record, when checked, every locally retained source binds.
    record = json.loads(
        (ROOT / "research/procedural-comparison-reading-20261028.json").read_bytes()
    )
    for source in record["records"]:
        assert digest(ROOT / source["candidate_cache_path"]) == source["sha256"]
