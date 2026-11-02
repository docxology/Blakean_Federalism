# Copyright (c) 2026 Daniel Ari Friedman
"""Retain two named same-duty contrasts without constructing an all-pairs ranking."""

import csv
import io
import json

from .institutional_review import ReviewReport
from .institutional_review_models import ProcedureId, ReviewInput, ReviewStudy
from .review_comparison import RepairRelation, compare_review
from .review_timing import MEMBER, RESIDENT
from .review_timing_models import TimingAtlas, TimingCell, TimingFigureData


class TimingContrast(ReviewInput):
    contrast_id: str
    stratum_id: str
    left: TimingCell
    right: TimingCell
    relation: RepairRelation


def timing_contrasts(atlas: TimingAtlas, data: TimingFigureData) -> tuple[TimingContrast, ...]:
    """Use the existing fixed-duty residual order on two named pairs, never across strata."""
    cells = {c.configuration.configuration_id: c for c in data.timeline_cells}
    records: list[TimingContrast] = []
    for name, left_id, right_id in (
        (
            "equal-resident-hours-different-position",
            "T.original-duty.r20.a06.automatic.s13.e20",
            "T.original-duty.r20.a06.automatic.s12.e19",
        ),
        (
            "early-threat-activation",
            "T.early-threat.r20.a06.automatic.s03.e20",
            "T.early-threat.r20.a06.on_filing.s03.e20",
        ),
    ):
        left, right = cells[ProcedureId(left_id)], cells[ProcedureId(right_id)]
        study = ReviewStudy(
            schema_version=1,
            baseline_decisions_sha256=atlas.specification.baseline_decisions_sha256,
            procedures=(left.review.procedure, right.review.procedure),
        )
        pair = compare_review(
            ReviewReport(schema_version=1, study=study, results=(left.review, right.review))
        )
        records.append(
            TimingContrast(
                contrast_id=name,
                stratum_id=left.configuration.stratum_id,
                left=left,
                right=right,
                relation=pair.comparisons[0].relation,
            )
        )
    return tuple(records)


def contrast_csv(records: tuple[TimingContrast, ...]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        (
            "contrast_id",
            "stratum_id",
            "left",
            "right",
            "relation",
            "claimant_id",
            "left_gaps",
            "right_gaps",
        )
    )
    for pair in records:
        for person in (MEMBER, RESIDENT):
            left = next(p for p in pair.left.review.claimants if p.claimant_id == person)
            right = next(p for p in pair.right.review.claimants if p.claimant_id == person)
            writer.writerow(
                (
                    pair.contrast_id,
                    pair.stratum_id,
                    pair.left.configuration.configuration_id,
                    pair.right.configuration.configuration_id,
                    pair.relation.value,
                    person,
                    json.dumps(left.uncovered_intervals),
                    json.dumps(right.uncovered_intervals),
                )
            )
    return stream.getvalue()
