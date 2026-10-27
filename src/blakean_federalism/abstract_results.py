# Copyright (c) 2026 Daniel Ari Friedman
"""Finite repair requirements and source-weighting sensitivity in measured vector plots."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .abstract_layout import AbstractSources, cell, footer, heading
from .figure_style import BLACK, GREY, RED, WHITE, circle, label, line

_OPERATOR_LABELS = (
    "Limit the identity claim",
    "Remove vision-based civic rank",
    "Establish equal personhood",
    "Allow overlapping affiliations",
    "Supply accessible public reasons",
    "Stipulate a separate charter",
    "Specify competence and enforcement",
    "Provide contestation and revision",
    "Support practical exit",
    "Include affected nonmembers",
    "Allocate resource burdens",
    "Address treaty and refusal",
)


def repair_page(c: Canvas, source: AbstractSources) -> None:
    result = source.repairs
    count = sum(bool(row.baseline_failed_rules) for row in result.cases)
    heading(
        c,
        f"Repair requirements in {count} modelled conflicts",
        (
            f"Essential interventions and admissible subsets of "
            f"{len(source.experiment.catalog)} declared operators."
        ),
    )
    rows = [row for row in result.cases if row.baseline_failed_rules]
    cell(c, "CLASSIFICATION RECORD", 20, 432, 137, 14, size=9, color=RED)
    cell(
        c,
        "Entity / role | issuer / warrant | reach / enforcement | consequence | review",
        159,
        432,
        361,
        24,
        size=9,
    )
    parts = (
        (result.baseline_admissible.admissible_subsets, BLACK, "Already admissible"),
        (result.baseline_failing.admissible_subsets, RED, "Repaired failing baseline"),
        (result.total_subsets - result.total_admissible_subsets, WHITE, "Still fails a predicate"),
    )
    x = 20.0
    for index, (count, color, title) in enumerate(parts):
        cell(
            c,
            f"{title}: {count:,}",
            20 + index * 168,
            399,
            164,
            25,
            size=9,
            color=RED if index == 1 else BLACK,
        )
        if result.total_subsets:
            width = 500 * count / result.total_subsets
            c.setFillColor(HexColor(color))
            c.setStrokeColor(HexColor(BLACK))
            c.setLineWidth(0.4)
            c.rect(x, 361, width, 9, stroke=1, fill=1)
            x += width
    cell(c, "CASE", 20, 344, 95, 16, size=9, color=RED)
    cell(c, "OPERATOR NUMBER", 129, 344, 238, 16, size=9, color=RED)
    cell(c, "MIN", 385, 344, 28, 16, size=9, color=RED)
    cell(c, "ADMISSIBLE / ALL", 420, 344, 100, 16, size=9, color=RED)
    catalog = source.experiment.catalog
    step = 238 / max(len(catalog), 1)
    for index, _ in enumerate(catalog):
        label(c, str(index + 1), 135 + index * step, 318, 8.6)
    for index, row in enumerate(rows):
        top = 301 - index * 29
        cell(c, row.decision_id, 20, top, 103, 17, size=9.6)
        for column, spec in enumerate(catalog):
            x = 135 + column * step
            if spec.intervention in row.essential_interventions:
                circle(c, x, top - 6, 2.8, BLACK, fill=BLACK, width=0.5)
            else:
                line(c, x - 2, top - 6, x + 2, top - 6, GREY, 0.6)
        minimum = "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality)
        cell(c, minimum, 385, top, 28, 17, size=10)
        cell(c, f"{row.admissible_subsets:,}/{row.subset_count:,}", 420, top, 100, 17, size=9.5)
        line(c, 20, top - 22, 520, top - 22, GREY, 0.4)
    if not rows:
        cell(c, "No failing baselines in this selection.", 20, 301, 500, 30)
    cell(
        c,
        "Filled dot: essential in every admissible subset. A dash means not essential.",
        20,
        147,
        500,
        17,
        size=9,
    )
    for index, spec in enumerate(catalog):
        column, row = divmod(index, 6)
        cell(
            c,
            (
                f"{index + 1:02d}  "
                f"{_OPERATOR_LABELS[list(type(spec.intervention)).index(spec.intervention)]}"
            ),
            20 + column * 254,
            126 - row * 13.5,
            246,
            14,
            size=8.8,
        )
    footer(
        c,
        (
            f"{result.total_subsets:,} labelled subsets across {len(result.cases)} alternatives; "
            f"{result.total_distinct_states} distinct records. Counts describe specified field "
            f"changes under fifteen predicates, not observed political outcomes."
        ),
    )
