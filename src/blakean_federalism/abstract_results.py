# Copyright (c) 2026 Daniel Ari Friedman
"""Name the conflicts and required field changes before showing exhaustive counts."""

from reportlab.lib.colors import HexColor
from reportlab.pdfgen.canvas import Canvas

from .abstract_layout import AbstractSources, cell, footer, heading
from .figure_style import BLACK, GREY, RED, WHITE, line

_CASE_NAMES = {
    "A-capture": "A: services tied to one nationality",
    "B-capture": "B: an association binds all co-nationals",
    "C-capture": "C: a new public claims coercive power",
    "D-capture": "D: vision rank determines civic rights",
    "E-capture": "E: water authority excludes affected people",
}


def repair_page(c: Canvas, source: AbstractSources) -> None:
    result = source.repairs
    rows = [row for row in result.cases if row.baseline_failed_rules]
    catalog = source.experiment.catalog
    combinations = 1 << len(catalog)
    checks = len(
        {state.code for row in source.experiment.decisions for state in row.baseline_rule_states}
    )
    heading(
        c,
        f"{len(rows)} conflict{' needs' if len(rows) == 1 else 's need'} different repairs",
        "Hypothetical decisions: name the changes, then count combinations passing the safeguards.",
    )
    stages = (
        ("1 SELECT", f"{len(catalog)} possible field changes"),
        ("2 APPLY", "Fixed persons, acts and affected groups"),
        ("3 ASSESS", f"All {checks} safeguards; one fixed rule set"),
        ("4 RECORD", "Passing selections + resulting case records"),
    )
    for index, (title, detail) in enumerate(stages):
        left = 20 + 130 * index
        c.setStrokeColor(HexColor(GREY))
        c.setFillColor(HexColor(WHITE))
        c.rect(left, 383, 110, 56, fill=1, stroke=1)
        cell(c, title, left + 5, 432, 100, 12, size=8.6, color=RED)
        cell(c, detail, left + 5, 414, 100, 30, size=8.5)
    cell(
        c,
        f"{combinations:,} combinations per alternative; not empirical probabilities.",
        20,
        379,
        500,
        11,
        size=8.6,
    )
    for x, width, value in (
        (20, 133, "FAILING DECISION"),
        (165, 226, "CHANGES REQUIRED IN EVERY PASSING COMBINATION"),
        (400, 28, "MIN"),
        (435, 85, f"PASSING / {combinations:,}"),
    ):
        cell(c, value, x, 364, width, 27, size=8.7, color=RED)
    labels = {spec.intervention: spec.label for spec in catalog}
    for index, row in enumerate(rows):
        top = 335 - index * 42
        cell(c, _CASE_NAMES.get(row.decision_id, row.decision_id), 20, top, 133, 38, size=9.2)
        required = "; ".join(labels[value] for value in row.essential_interventions)
        if not row.admissible_subsets:
            required = "No selection passes the stated checks."
        elif not required:
            required = "Alternative repairs share no required change."
        cell(c, required, 165, top, 226, 38, size=9.1)
        minimum = "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality)
        cell(c, minimum, 400, top, 28, 18, size=10)
        cell(c, f"{row.admissible_subsets:,}/{row.subset_count:,}", 435, top, 85, 18, size=9.1)
        c.setFillColor(HexColor(WHITE))
        c.setStrokeColor(HexColor(GREY))
        c.setLineWidth(0.4)
        c.rect(435, top - 27, 80, 4, fill=1, stroke=1)
        if row.admissible_subsets:
            c.setFillColor(HexColor(RED))
            c.rect(
                435,
                top - 27,
                80 * row.admissible_subsets / row.subset_count,
                4,
                fill=1,
                stroke=0,
            )
        line(c, 20, top - 40, 520, top - 40, GREY, 0.4)
    if not rows:
        cell(c, "No failing starting records in this selection.", 20, 335, 500, 30)
    parts = (
        (result.baseline_admissible.admissible_subsets, BLACK, "Already-passing starts"),
        (result.baseline_failing.admissible_subsets, RED, "Passing after repair"),
        (result.total_subsets - result.total_admissible_subsets, WHITE, "Still failing"),
    )
    left = 20.0
    for index, (count, color, title) in enumerate(parts):
        cell(
            c,
            f"{title}: {count:,}",
            20 + index * 168,
            115,
            164,
            25,
            size=8.7,
            color=RED if index == 1 else BLACK,
        )
        if result.total_subsets:
            width = 500 * count / result.total_subsets
            c.setFillColor(HexColor(color))
            c.setStrokeColor(HexColor(BLACK))
            c.setLineWidth(0.4)
            c.rect(left, 82, width, 8, fill=1, stroke=1)
            left += width
    cell(
        c,
        (
            f"{result.total_subsets:,} labelled combinations across "
            f"{len(result.cases)} alternatives; "
            f"{result.total_distinct_states} distinct resulting records. MIN counts changes; "
            "combinations can produce the same record."
        ),
        20,
        74,
        500,
        30,
        size=9.2,
    )
    footer(
        c,
        "Catalog: " + "; ".join(spec.intervention.value.replace("_", " ") for spec in catalog) + "."
        if catalog
        else "The catalog is empty; the empty selection is the only combination.",
    )
