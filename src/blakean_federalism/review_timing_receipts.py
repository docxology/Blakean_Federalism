# Copyright (c) 2026 Daniel Ari Friedman
"""Bind analytical completion separately from installed, native and release acceptance."""

import sys
from collections.abc import Mapping
from importlib import metadata
from pathlib import Path
from typing import Literal

import blake
from blake.methods.producer import SourceBinding, source_hashes

from .institutional_review_models import ReviewInput
from .models import Assessment, Digest, FileReceipt
from .review_comparison_run import SHARED


class TimingRuntime(ReviewInput):
    python: str
    prefix: str
    base_prefix: str
    sdk_source_version: str
    sdk_module_path: str
    sdk_distribution_version: str
    sdk_direct_url: str | None


class TimingReceipt(ReviewInput):
    schema_version: Literal[1] = 1
    producer_version: str
    producer_state: Literal["artifacts_complete"] = "artifacts_complete"
    runtime: TimingRuntime
    command: tuple[str, ...]
    inputs: tuple[FileReceipt, ...]
    baseline_assessments: tuple[Assessment, ...]
    producers: dict[str, Digest]
    outputs: tuple[FileReceipt, ...]
    configurations: int
    person_records: int
    scope: str = (
        "Complete source-bound stipulated atlas. External command receipts establish actual "
        "process termination; installed-Git, native manuscript, scholarly and release "
        "acceptance require separate exact-bound evidence."
    )


def timing_runtime() -> TimingRuntime:
    distribution = metadata.distribution("blake")
    return TimingRuntime(
        python=sys.version,
        prefix=sys.prefix,
        base_prefix=sys.base_prefix,
        sdk_source_version=blake.__version__,
        sdk_module_path=str(Path(blake.__file__).resolve()),
        sdk_distribution_version=distribution.version,
        sdk_direct_url=distribution.read_text("direct_url.json"),
    )


def timing_producers(*, figures: bool) -> Mapping[str, str]:
    """Bind local policy/evaluation and the delegated interval/storage source closure."""
    local = (
        "__init__.py",
        "review_timing_models.py",
        "review_timing_inputs.py",
        "review_timing_grid.py",
        "review_timing.py",
        "review_timing_exports.py",
        "review_timing_captions.py",
        "review_timing_contrasts.py",
        "review_timing_receipts.py",
        "review_timing_cli.py",
        "review_timing_run.py",
        "institutional_review.py",
        "institutional_review_models.py",
        "review_inputs.py",
        "review_comparison.py",
        "review_comparison_run.py",
        "review_pressure.py",
        "review_pressure_models.py",
        "institutions.py",
        "models.py",
        "storage.py",
    )
    extra = (
        (
            "review_timing_figure.py",
            "review_timing_readiness_figure.py",
            "review_timing_protection_figure.py",
            "figure_style.py",
            "resources/fonts/Vera.ttf",
            "resources/fonts/bitstream-vera-license.txt",
        )
        if figures
        else ()
    )
    return source_hashes(
        (SourceBinding("blakean_federalism", local + extra), SourceBinding("blake", SHARED))
    )
