# Copyright (c) 2026 Daniel Ari Friedman
"""An exact requirement-set display and pairwise comparison of fixed procedures."""

import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Final

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from .figure_style import BLACK, GREY, MUTED, RED, label, line, registry, text
from .models import ResearchError
from .review_comparison import ClaimantRequirements, RepairRelation, ReviewComparison

FIGURE_NAMES: Final = ("review-requirements", "review-comparability")
_SIZE: Final = (540, 610)
_PROCEDURES: Final = 14
_PEOPLE: Final = 2


def _person_label(person: ClaimantRequirements) -> str:
    parts = [requirement.value.replace("_", " ") for requirement in person.unmet]
    if person.preparation_shortfall_hours:
        parts.append(f"shortfall {person.preparation_shortfall_hours} h")
    if person.readiness_lateness_hours:
        parts.append(f"late {person.readiness_lateness_hours} h")
    parts.extend(f"gap [{start},{end}) h" for start, end in person.uncovered_intervals)
    return "; ".join(parts) or "empty"


def _requirements(canvas: Canvas, report: ReviewComparison) -> None:
    text(canvas, "What each procedure still requires", 16, 593, 508, 18)
    text(
        canvas,
        "Residual requirement sets · the person and exact interval remain attached",
        16,
        562,
        508,
        9,
    )
    line(canvas, 16, 539, 524, 539, RED, 1.5)
    text(canvas, "ID", 16, 528, 45, 8, MUTED)
    people = report.requirements[0].claimants
    for x, person in zip((67, 215), people, strict=True):
        text(canvas, person.claimant_id, x, 528, 142, 9)
    text(canvas, "FORUM", 385, 528, 139, 8, MUTED)
    for i, row in enumerate(report.requirements):
        y = 500 - i * 28
        text(canvas, row.procedure_id, 16, y, 45, 9, RED)
        indexed = {p.claimant_id: p for p in row.claimants}
        for x, person in zip((67, 215), people, strict=True):
            value = _person_label(indexed[person.claimant_id])
            text(
                canvas,
                value,
                x,
                y,
                142,
                8,
                MUTED if value == "empty" else BLACK,
            )
        forum = "; ".join(requirement.value.replace("_", " ") for requirement in row.unmet_forum)
        text(canvas, forum or "empty", 385, y, 139, 8)
        line(canvas, 16, y - 23, 524, y - 23, GREY, 0.4)
    text(canvas, "MINIMAL RESIDUAL PROFILES IN THIS FIXED FAMILY", 16, 96, 508, 8, RED)
    text(canvas, ", ".join(report.frontier_procedure_ids), 16, 81, 508, 10)
    text(
        canvas,
        "Empty = no unmet modeled requirement, not a certification of freedom.",
        16,
        59,
        508,
        8.5,
    )
    flagged = "; ".join(
        f"{r.procedure.procedure_id}: "
        + ", ".join(issue.value.replace("_", " ") for issue in r.procedure.unassessed_issues)
        for r in report.review.results
        if r.procedure.unassessed_issues
    )
    text(
        canvas, "OUTSIDE THE ORDER / " + (flagged or "no issue flags declared"), 16, 39, 508, 8, RED
    )


def _symbol(relation: RepairRelation) -> str:
    match relation:
        case RepairRelation.EQUIVALENT:
            return "="
        case RepairRelation.LEFT_SUBSET:
            return "<"
        case RepairRelation.RIGHT_SUBSET:
            return ">"
        case RepairRelation.INCOMPARABLE:
            return "x"


def _comparability(canvas: Canvas, report: ReviewComparison) -> None:
    text(canvas, "Many procedural tradeoffs remain incomparable", 16, 593, 508, 17)
    counts = Counter(pair.relation for pair in report.comparisons)
    text(
        canvas,
        "".join(
            (
                f"{len(report.comparisons)} unordered pairs · ",
                f"{counts[RepairRelation.INCOMPARABLE]} incomparable · ",
                f"{counts[RepairRelation.EQUIVALENT]} equivalent",
            )
        ),
        16,
        562,
        508,
        9,
    )
    line(canvas, 16, 539, 524, 539, RED, 1.5)
    rows = report.requirements
    lookup = {(p.left, p.right): p.relation for p in report.comparisons}
    for i, row in enumerate(rows):
        position = 108 + i * 29
        label(canvas, row.procedure_id, position, 514, 8)
        label(canvas, row.procedure_id, 38, 488 - i * 25, 9)
        for j, column in enumerate(rows):
            if i == j:
                symbol = "="
            elif i < j:
                symbol = _symbol(lookup[(row.procedure_id, column.procedure_id)])
            else:
                symbol = _symbol(lookup[(column.procedure_id, row.procedure_id)]).translate(
                    str.maketrans("<>", "><")
                )
            label(canvas, symbol, 108 + j * 29, 488 - i * 25, 10, RED if symbol == "x" else BLACK)
        line(canvas, 65, 480 - i * 25, 514, 480 - i * 25, GREY, 0.4)
    text(canvas, "READ ROW RELATIVE TO COLUMN", 16, 113, 508, 8, RED)
    text(
        canvas,
        "<  row requires a proper subset     >  column requires a proper subset",
        16,
        97,
        508,
        9,
    )
    text(
        canvas,
        "=  same residual profile     x  neither requirement profile contains the other",
        16,
        79,
        508,
        8.5,
    )
    text(
        canvas,
        "Compare each person's categories, deficits and exact gaps, then forum requirements.",
        16,
        59,
        508,
        8,
    )
    text(
        canvas,
        "Equal hours at different times can be incomparable; raw records remain available.",
        16,
        35,
        508,
        8,
    )


def validate_comparison_figures(report: ReviewComparison) -> str:
    """Reject unsupported layouts and missing rasterizers before reserving output."""
    if len(report.requirements) != _PROCEDURES or any(
        len(p.claimants) != _PEOPLE for p in report.requirements
    ):
        raise ResearchError(
            "comparison_figure_layout", "Require the fixed fourteen procedures and two people"
        )
    executable = shutil.which("pdftoppm")
    if executable is None:
        raise ResearchError("pdftoppm_missing", "Comparison figures need the native rasterizer")
    return executable


def render_comparison_figures(report: ReviewComparison, output: Path) -> tuple[Path, ...]:
    """Generate deterministic vector masters and raster derivatives from this exact report."""
    rasterizer = validate_comparison_figures(report)
    fonts = Path(__file__).parent / "resources/fonts"
    registry(pdfmetrics).registerFont(TTFont("BF-Vera", str(fonts / "Vera.ttf")))
    output.mkdir(parents=True, exist_ok=False)
    paths: list[Path] = []
    for name, draw in zip(FIGURE_NAMES, (_requirements, _comparability), strict=True):
        pdf = output / (name + ".pdf")
        canvas = Canvas(str(pdf), pagesize=_SIZE, invariant=1)
        draw(canvas, report)
        canvas.showPage()
        canvas.save()
        _ = subprocess.run(  # noqa: S603 -- Resolved binary, explicit paths, no shell.
            [rasterizer, "-singlefile", "-scale-to", "2400", "-png", str(pdf), str(output / name)],
            check=True,
            capture_output=True,
        )
        paths.extend((pdf, output / (name + ".png")))
    return tuple(paths)


def comparison_captions(report: ReviewComparison) -> dict[str, str]:
    """Bind manuscript captions to the same data as both new figures."""
    counts = Counter(pair.relation for pair in report.comparisons)
    return {
        "REVIEW_REQUIREMENTS_CAPTION": (
            f"Residual requirements for {len(report.requirements)} stipulated procedures and "
            f"{sum(len(p.claimants) for p in report.requirements)} claimant records. "
            "Each row retains admission, remaining affiliated, preparation shortfall, deadline "
            "lateness and exact half-open uncovered intervals for the named person; issuer "
            "separation and revision belong to the forum. Empty profiles are minimal in this "
            f"family: {', '.join(report.frontier_procedure_ids)}. H12's retaliation and disputed "
            "forum competence remain outside the order. These are conditions to discharge, "
            "not independently costed policy actions."
        ),
        "REVIEW_COMPARISON_CAPTION": (
            f"All {len(report.comparisons)} unordered procedure pairs under the person-indexed "
            f"requirement order: {counts[RepairRelation.INCOMPARABLE]} incomparable, "
            f"{counts[RepairRelation.EQUIVALENT]} equivalent, and "
            f"{counts[RepairRelation.LEFT_SUBSET] + counts[RepairRelation.RIGHT_SUBSET]} "
            "strictly comparable. Read row relative to column: < requires a proper subset, "
            "> requires a proper superset, = means the same residual profile, and x means "
            "neither contains the other. H06 and H07 have equal uncovered durations at "
            "different times and are incomparable. Equivalence concerns modeled residual "
            "requirements, not identical procedures or equivalent political legitimacy."
        ),
    }
