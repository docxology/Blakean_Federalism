# Copyright (c) 2026 Daniel Ari Friedman
"""Conditional paper inputs, dependency pins and late local producers stay in custody."""

import pytest

from blakean_federalism import __version__
from blakean_federalism.method_provenance import shared_source_hashes
from blakean_federalism.models import ResearchError
from blakean_federalism.publication_contract import source_bindings
from blakean_federalism.publication_sources import (
    SOURCE_NAMES,
    publication_source_names,
    verify_delegated_producers,
)
from blakean_federalism.review_timing_inputs import INPUT_NAMES


def test_source_policy_includes_both_dependency_files_and_dynamic_local_producers(tmp_path):
    producer = tmp_path / "src/blakean_federalism/new_domain.py"
    producer.parent.mkdir(parents=True)
    producer.write_text("pass\n")
    names = publication_source_names(tmp_path, "![Timing](a.png){#fig:review-timing-readiness}")
    assert set(INPUT_NAMES) <= set(names)
    assert {"pyproject.toml", "uv.lock"} <= set(names)
    assert producer.relative_to(tmp_path).as_posix() in names
    assert names[:5] == SOURCE_NAMES[:5]
    assert "research/review-timing-atlas-v1.json" not in publication_source_names(tmp_path, "")


def test_new_required_pin_cannot_be_silently_omitted(tmp_path):
    names = publication_source_names(tmp_path, "")
    for name in names:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"retained")
    before = source_bindings(tmp_path, names)
    assert "uv.lock" in before
    (tmp_path / "uv.lock").write_bytes(b"changed")
    assert before != source_bindings(tmp_path, names)
    (tmp_path / "uv.lock").rename(tmp_path / "retained-old.lock")
    with pytest.raises((ResearchError, FileNotFoundError)):
        source_bindings(tmp_path, names)


def test_current_producer_requires_exact_actual_sdk_and_archival_absence_is_retained():
    producers = shared_source_hashes()
    verify_delegated_producers(__version__, producers)
    verify_delegated_producers("0.18.0", {})
    with pytest.raises(ResearchError, match="publication_producer_changed"):
        verify_delegated_producers(__version__, {})
    producers.pop(next(iter(producers)))
    with pytest.raises(ResearchError, match="publication_producer_changed"):
        verify_delegated_producers(__version__, producers)
