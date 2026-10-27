# Copyright (c) 2026 Daniel Ari Friedman
"""Four source-bound visual essays combining original plates, verse and analysis."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import FOCUS
from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, MUTED, RED, circle, curve, label, line
from .illuminated_style import arrow, footer, heading, plate, prose, register_serif_fonts
from .institutional_experiment_models import InstitutionalExperiment
from .manuscript import Quotation
from .models import ResearchError
from .workbench_models import Workbench

_MAX_BASELINES = 5

_REQUIRED_ART = frozenset({"J1", "J52", "J55", "J91"})
_QUOTE_LENGTHS = {"Q03": 2, "Q05": 4, "Q13": 1, "Q14": 4, "Q16": 1, "Q18": 2, "Q23": 1, "Q31": 1}


@dataclass(frozen=True)
class _Sources:
    report: Workbench
    artwork: Mapping[str, Path]
    quotations: Mapping[str, Quotation]
    statistics: CorpusStatistics
    experiment: InstitutionalExperiment

    def verse(self, quote_id: str, start: int = 0, stop: int | None = None) -> str:
        return " ".join(s.text for s in self.quotations[quote_id].segments[start:stop])


def illuminated_drawings(
    report: Workbench, artwork: Mapping[str, Path]
) -> dict[str, Callable[[Canvas], None]]:
    """Require real artwork, recorded verse and analytical inputs before drawing any page."""
    missing = _REQUIRED_ART - artwork.keys()
    if missing:
        raise ResearchError("figure_artwork", ", ".join(sorted(missing)))
    for key in sorted(_REQUIRED_ART):
        if not artwork[key].is_file():
            raise ResearchError("figure_artwork", key)
    quotes = {q.quote_id: q for q in report.quotations}
    for key, count in _QUOTE_LENGTHS.items():
        if key not in quotes or len(quotes[key].segments) < count:
            raise ResearchError("figure_quotation", key)
    stats, experiment = report.corpus_statistics, report.institutional_experiments
    if stats is None or experiment is None:
        raise ResearchError(
            "publication_statistics", "Statistics and intervention results required"
        )
    if not set(FOCUS) <= {q.query_id for q in stats.queries}:
        raise ResearchError("figure_queries", "Eight declared comparison queries required")
    failed = [row for row in experiment.decisions if row.baseline_failed_rules]
    if len(failed) > _MAX_BASELINES:
        raise ResearchError("figure_case_layout", "At most five failed baselines fit this figure")
    register_serif_fonts()
    source = _Sources(report, dict(artwork), quotes, stats, experiment)
    return {
        "abstract-1": partial(_composition, source=source),
        "abstract-2": partial(_scholarship, source=source),
        "abstract-3": partial(_decision, source=source),
        "abstract-4": partial(_evidence, source=source),
    }


def _composition(c: Canvas, source: _Sources) -> None:
    heading(
        c,
        "01",
        "Composition without capture",
        "Persons endure; affiliations change; authority answers for its acts.",
    )
    plate(c, source.artwork["J1"], (20, 434, 184, 258))
    # A pointed red arch echoes the depicted threshold without painting over the plate.
    line(c, 14, 176, 14, 435, RED, 0.6)
    curve(c, (14, 435, 52, 436, 86, 441, 112, 441), RED, 0.6)
    curve(c, (112, 441, 138, 441, 172, 436, 210, 435), RED, 0.6)
    line(c, 210, 435, 210, 176, RED, 0.6)
    prose(c, "Jerusalem I, plate 1. Lamp, figure and threshold.", (20, 168, 184, 27), size=9)
    prose(c, source.verse("Q13"), (20, 133, 184, 49), size=13, font="BF-Serif-Italic")
    prose(c, "Marriage 7 / E36 (Q13)", (20, 85, 184, 12), size=9, color=MUTED)
    rows = (
        (
            434,
            "PERSONS / P",
            source.verse("Q03", 1, 2),
            "Milton 32:23 / E132 (Q03)",
            "A person exceeds every assigned role and collective label.",
        ),
        (
            326,
            "POETIC STATES / S",
            source.verse("Q05", 0, 2),
            "Jerusalem 52 / E200 (Q05)",
            "Enduring possibilities become intelligible through particular lives.",
        ),
        (
            218,
            "NATIONAL FORMATIONS / N",
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            "Plural histories and exchanges compose a common world.",
        ),
    )
    for top, title, verse, locator, interpretation in rows:
        prose(c, title, (229, top, 291, 14), size=10, color=RED)
        prose(c, verse, (229, top - 19, 291, 38), size=14, font="BF-Serif-Italic")
        prose(c, locator, (229, top - 59, 291, 12), size=9, color=MUTED)
        prose(c, interpretation, (229, top - 75, 291, 26), size=9.5)
    line(c, 229, 105, 520, 105, RED, 0.7)
    _relations(c)
    prose(
        c,
        "C: J to D / claimed competence; require warrant, reach and review.",
        (229, 66, 291, 26),
        size=9,
        color=RED,
    )
    footer(
        c,
        "".join(
            (
                f"{source.report.source_units:,} imported units; ",
                f"{source.statistics.primary_source_units:,} primary extracts. Art: Library ",
                "of Congress, Jerusalem I, c.1832?, item 48038103; uncropped.",
            ),
        ),
    )


def _relations(c: Canvas) -> None:
    for x, text_value in ((245, "P"), (367, "N"), (500, "S")):
        label(c, text_value, x, 91, 9)
    for x, y, end_x, end_y, dashed in (
        (237, 82, 359, 82, False),
        (253, 72, 359, 82, False),
        (253, 72, 375, 72, False),
        (359, 82, 492, 82, True),
        (375, 72, 492, 82, True),
        (375, 72, 508, 72, True),
    ):
        c.saveState()
        if dashed:
            c.setDash(2, 2)
        line(c, x, y, end_x, end_y, BLACK, 0.6)
        c.restoreState()
    for x, y in ((237, 82), (253, 72), (359, 82), (375, 72), (492, 82), (508, 72)):
        circle(c, x, y, 3, BLACK)
    label(c, "A / affiliation", 305, 91, 9, RED)
    label(c, "I / interpretation", 436, 91, 9, RED)


def _scholarship(c: Canvas, source: _Sources) -> None:
    heading(
        c,
        "02",
        "Read the tension; specify the claim",
        "Poetic assertions, scholarly disagreements and institutional questions stay connected.",
    )
    plate(c, source.artwork["J52"], (20, 433, 133, 187))
    prose(c, source.verse("Q05", 2, 4), (20, 237, 133, 61), size=13, font="BF-Serif-Italic")
    prose(c, "Jerusalem 52 / E200 (Q05)", (20, 173, 133, 24), size=9, color=MUTED)
    prose(
        c,
        """State is not person. Interpretation is not jurisdiction. A represented
identity does not authorize its interpreter to rule.""",
        (20, 132, 133, 80),
        size=10,
        font="BF-Serif",
    )
    panels = (
        (
            433,
            source.verse("Q03", 0, 1),
            "Milton 32:22 / E132 (Q03)",
            "Damrosch, pp.15-21: universality in particular forms.",
            "Lee, pp.1-10: identity resists compulsory remaking.",
            "What changes while a person's standing persists?",
        ),
        (
            304,
            source.verse("Q14", 2, 4),
            "Jerusalem 27:87-88 / E173 (Q14)",
            "Fallon, ms.pp.10-12: national opening and incorporation.",
            "Mellor, pp.148-153: creative reciprocity retains hierarchy.",
            "Who interprets, refuses an assigned role and governs?",
        ),
        (
            175,
            source.verse("Q31"),
            "Jerusalem 11:5 / E154 (Q31)",
            "Simpson, pp.67-78: refusal limits compulsory disclosure.",
            "Shachar, pp.75-77: review before enforceability.",
            "Who can contest the protective forum itself?",
        ),
    )
    for index, (top, verse, locator, first, second, question) in enumerate(panels):
        prose(c, verse, (173, top, 347, 36), size=13, font="BF-Serif-Italic")
        prose(c, locator, (173, top - 37, 347, 12), size=9, color=MUTED)
        prose(c, first, (173, top - 55, 166, 34), size=9)
        prose(c, second, (354, top - 55, 166, 34), size=9)
        prose(c, question, (173, top - 95, 347, 25), size=10, color=RED)
        if index < len(panels) - 1:
            line(c, 173, top - 124, 520, top - 124, BLACK, 0.4)
    footer(
        c,
        """Arguments guide the questions below each pair. Art: Jerusalem I, plate 52,
Library of Congress, c.1832?, item 48038103; uncropped.""",
    )


def _decision(c: Canvas, source: _Sources) -> None:
    heading(
        c,
        "03",
        "Make authority answerable",
        "A hypothetical water levy: name the decision, its reach, its burden and its remedy.",
    )
    plate(c, source.artwork["J55"], (20, 432, 140, 198))
    prose(c, source.verse("Q16", 0, 1), (20, 224, 140, 72), size=13, font="BF-Serif-Italic")
    prose(c, "Jerusalem 55:51 / E205 (Q16)", (20, 149, 140, 23), size=9, color=MUTED)
    prose(c, source.verse("Q23"), (20, 118, 140, 58), size=11, font="BF-Serif-Italic")
    prose(c, "Jerusalem 73:49 / E229 (Q23)", (20, 57, 140, 12), size=9, color=MUTED)
    cells = (
        (180, 432, "ENTITY", "Person, public or collective affected by the levy."),
        (360, 432, "ASSIGNED ROLE", "User, worker, resident or treaty claimant."),
        (
            180,
            350,
            "ISSUER + JURISDICTION",
            "Board names its charter, territory and reviewable competence.",
        ),
        (
            360,
            350,
            "PROPOSED ACT + WARRANT",
            "Levy, period, reasons and claimed C relation to the act.",
        ),
        (
            180,
            268,
            "REACH / ENFORCER",
            "Upstream, downstream and nonmembers. Name enforcing actor and coercive limits.",
        ),
        (360, 268, "CONSEQUENCE", "Water access, payment burden, residual harm and who bears it."),
    )
    for x, top, title, detail in cells:
        line(c, x, top, x + 160, top, RED, 1)
        prose(c, title, (x, top - 8, 160, 23), size=9, color=RED)
        prose(c, detail, (x, top - 33, 160, 39), size=10, font="BF-Serif")
    for y in (395, 313, 231):
        arrow(c, (343, y), (357, y))
    arrow(c, (439, 360), (439, 350))
    arrow(c, (260, 278), (260, 268))
    line(c, 180, 181, 520, 181, RED, 1)
    prose(
        c, "CHALLENGE / INTERIM DUTIES / EFFECTIVE REMEDY", (180, 172, 340, 25), size=10, color=RED
    )
    prose(
        c,
        """Fund participation. Maintain essential water during review. Name the
reviewer, deadline, binding remedy and route to challenge the forum itself.""",
        (180, 143, 340, 40),
        size=11,
        font="BF-Serif",
    )
    arrow(c, (176, 115), (169, 115))
    arrow(c, (169, 115), (169, 313), dashed=True)
    arrow(c, (169, 313), (177, 313))
    prose(c, "RECORD -> CHECK -> REVISE", (180, 92, 340, 14), size=10, color=RED)
    prose(c, "EXCLUDED_AFFECTED / RESOURCE_GAP / CONTESTATION", (180, 71, 340, 24), size=9)
    footer(
        c,
        """Accountability map: classification, competence, reach, enforcement and remedy.
Art: Jerusalem I, plate 55, Library of Congress, c.1832?; uncropped.""",
    )


def _evidence(c: Canvas, source: _Sources) -> None:
    heading(
        c,
        "04",
        "Read particulars; compare the records",
        "Corpus measurements direct close reading; synthetic interventions test declared rules.",
    )
    stats = source.statistics
    plate(c, source.artwork["J91"], (20, 431, 130, 171))
    prose(c, source.verse("Q18", 0, 2), (20, 250, 130, 88), size=10.5, font="BF-Serif-Italic")
    prose(c, "Jerusalem 91:26-27 / E251 (Q18)", (20, 158, 130, 24), size=9, color=MUTED)
    prose(
        c,
        "".join(
            (
                f"{source.report.source_units:,} units imported; ",
                f"{stats.primary_source_units:,} primary extracts",
            ),
        ),
        (170, 432, 350, 30),
        size=12,
        font="BF-Serif-Bold",
    )
    prose(
        c,
        f"{stats.primary_tokens:,} tokens / {stats.primary_work_groups} source families",
        (170, 397, 350, 14),
        size=10,
    )
    _rates(c, stats)
    _repairs(c, source.experiment)
    footer(
        c,
        """Rates retain copies; equal-family means weight positive-token families
equally. Art: Jerusalem I, plate 91, Library of Congress, c.1832?;
uncropped.""",
    )


def _rates(c: Canvas, stats: CorpusStatistics) -> None:
    columns = (
        (170, 82, "QUERY"),
        (255, 43, "HITS"),
        (303, 94, "UNITS / FAMILIES"),
        (401, 119, "RATES / 10,000"),
    )
    for x, width, title in columns:
        prose(c, title, (x, 376, width, 22), size=9, color=RED)
    prose(c, "Matched / total", (303, 352, 94, 12), size=9, color=MUTED)
    prose(c, "Pooled / equal mean", (401, 352, 119, 12), size=9, color=MUTED)
    lookup = {q.query_id: q for q in stats.queries}
    for index, key in enumerate(FOCUS):
        query = lookup[key]
        measure = query.copy_retaining
        families = sum(
            any(q.query_id == key and q.measure.occurrences > 0 for q in st.queries)
            for st in stats.strata
            if st.dimension == "work"
        )
        rate, balanced = measure.rate_per_10000_tokens, query.work_balanced_rate_per_10000_tokens
        values = (
            key,
            f"{measure.occurrences:,}",
            "".join(
                (
                    f"{measure.matched_units}/{measure.source_units} / ",
                    f"{families}/{stats.primary_work_groups}",
                ),
            ),
            "N/A" if rate is None or balanced is None else f"{rate:.2f} / {balanced:.2f}",
        )
        y = 333 - index * 18
        for (x, width, _), value in zip(columns, values, strict=True):
            prose(c, value, (x, y, width, 15), size=9, color=RED if value == values[-1] else BLACK)
    positive = len({unit.work_id for unit in stats.units if unit.tokens > 0})
    prose(
        c,
        f"Equal mean: {positive} positive-token families. Presence and hits counted separately.",
        (170, 183, 350, 25),
        size=9,
        color=MUTED,
    )


def _repairs(c: Canvas, experiment: InstitutionalExperiment) -> None:
    line(c, 20, 133, 520, 133, RED, 1)
    prose(
        c,
        "FINITE INTERVENTIONS / failed baseline -> minimum interventions",
        (20, 126, 500, 16),
        size=10,
        color=RED,
    )
    rows = [row for row in experiment.decisions if row.baseline_failed_rules]
    for index, row in enumerate(rows):
        x = 20 + index * 100
        name = row.decision_id.split("-")[0]
        minimum = "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality)
        prose(c, f"{name}  {minimum}", (x, 104, 92, 25), size=15, font="BF-Serif-Bold")
        count = len(row.baseline_failed_rules)
        prose(c, f"{count} failed rule" + ("s" if count != 1 else ""), (x, 85, 92, 13), size=9)
        prose(c, f"admit {row.admissible_subsets}/{row.subset_count}", (x, 71, 92, 13), size=9)
    prose(
        c,
        "".join(
            (
                f"All {len(experiment.decisions)} alternatives: ",
                f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                f"admissible subsets; {experiment.total_distinct_states:,} distinct records.",
            ),
        ),
        (20, 53, 500, 12),
        size=9,
        color=MUTED,
    )
