# Copyright (c) 2026 Daniel Ari Friedman
"""Publish one source-bound timing epoch with exclusive outputs and a final receipt."""

import sys
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING

from . import __version__
from .models import FileReceipt, ResearchError
from .review_timing import atlas_from_inputs, timing_figure_data, timing_summary
from .review_timing_captions import timing_captions
from .review_timing_contrasts import contrast_csv, timing_contrasts
from .review_timing_exports import claimant_csv
from .review_timing_inputs import load_timing_inputs
from .review_timing_models import TimingAtlas
from .review_timing_receipts import TimingReceipt, timing_producers, timing_runtime
from .storage import digest, safe_path, verify_file, write_new

if TYPE_CHECKING:
    from collections.abc import Callable


def publish_timing(root: Path, output: Path, *, figures: bool = False) -> TimingAtlas:
    """Check all inputs before reserving a run; keep any failed partial epoch inspectable."""
    private = (root / "analysis_output").resolve()
    if output.resolve() == private or not output.resolve().is_relative_to(private):
        raise ResearchError("timing_private_output", "Choose a new analysis_output child")
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ResearchError("timing_symlink_output", str(output))
    if output.exists():
        raise ResearchError("occupied_output", str(output))
    inputs = load_timing_inputs(root)
    producers = dict(timing_producers(figures=figures))
    runtime = timing_runtime()
    atlas = atlas_from_inputs(inputs)
    summary = timing_summary(atlas)
    data = timing_figure_data(atlas)
    captions = timing_captions(summary, data)
    contrasts = timing_contrasts(atlas, data)
    renderer: Callable[[TimingAtlas, Path], tuple[Path, ...]] | None = None
    if figures:
        from .review_timing_figure import (  # noqa: PLC0415 -- Optional manuscript capability.
            render_timing_figures,
            validate_timing_figures,
        )

        validate_timing_figures(atlas)
        renderer = render_timing_figures
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "atlas-spec.json", inputs.files[0].content.decode("utf-8"))
    write_new(
        output / "atlas-configurations.jsonl",
        "".join(c.configuration.model_dump_json(round_trip=True) + "\n" for c in atlas.cells),
    )
    write_new(output / "atlas-claimants.csv", claimant_csv(atlas))
    write_new(output / "atlas-summary.json", summary.model_dump_json(indent=2) + "\n")
    write_new(output / "atlas-selected-contrasts.csv", contrast_csv(contrasts))
    write_new(output / "figure-data.json", data.model_dump_json(indent=2, round_trip=True) + "\n")
    write_new(output / "captions.json", captions.model_dump_json(indent=2) + "\n")
    if renderer is not None:
        _ = renderer(atlas, output / "figures")
    if any(safe_path(root, f.name).read_bytes() != f.content for f in inputs.files):
        raise ResearchError("timing_changed_inputs", "No completion after changed input bytes")
    if producers != timing_producers(figures=figures):
        raise ResearchError("timing_changed_producer", "No completion after changed producer bytes")
    outputs = tuple(
        FileReceipt(path=p.relative_to(output).as_posix(), size=p.stat().st_size, sha256=digest(p))
        for p in sorted(output.rglob("*"))
        if p.is_file()
    )
    receipt = TimingReceipt(
        producer_version=__version__,
        runtime=runtime,
        command=tuple(sys.argv),
        inputs=tuple(
            FileReceipt(path=f.name, size=len(f.content), sha256=sha256(f.content).hexdigest())
            for f in inputs.files
        ),
        baseline_assessments=atlas.baseline_assessments,
        producers=producers,
        outputs=outputs,
        configurations=summary.configurations,
        person_records=summary.person_records,
    )
    write_new(output / "atlas-receipt.json", receipt.model_dump_json(indent=2) + "\n")
    return atlas


def verify_timing_output(output: Path, expected_receipt_sha256: str) -> TimingReceipt:
    """Require a caller-held final receipt and exact complete output membership."""
    receipt_path = safe_path(output, "atlas-receipt.json")
    if digest(receipt_path) != expected_receipt_sha256:
        raise ResearchError("timing_receipt_pin", "Final receipt differs from the caller-held pin")
    receipt = TimingReceipt.model_validate_json(receipt_path.read_bytes())
    names = {f.path for f in receipt.outputs}
    if len(names) != len(receipt.outputs):
        raise ResearchError("timing_duplicate_output", "Output receipt names must be unique")
    actual = {
        p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() or p.is_symlink()
    }
    if actual != names | {"atlas-receipt.json"}:
        raise ResearchError("timing_output_membership", "Missing or additional output")
    for entry in receipt.outputs:
        _ = verify_file(output, entry.path, entry.size, entry.sha256)
    return receipt
