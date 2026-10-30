# Copyright (c) 2026 Daniel Ari Friedman
"""Source-bound institutional and measurement pages for illuminated abstracts."""

from reportlab.pdfgen.canvas import Canvas

from .analysis_figures import FOCUS
from .corpus_statistics_models import CorpusStatistics
from .figure_style import BLACK, MUTED, RED, line
from .illuminated_sources import IlluminatedSources
from .illuminated_style import arrow, footer, heading, plate, prose
from .institutional_experiment_models import InstitutionalExperiment
from .publication_body import record_arrow


def draw_decision(c: Canvas, source: IlluminatedSources) -> None:
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
        (
            180,
            432,
            "ENTITY / ROLE",
            "Person, worker, resident or treaty claimant affected by the levy.",
        ),
        (360, 432, "ISSUER / WARRANT", "Board, charter and reviewable claim of competence."),
        (
            180,
            260,
            "REACH / ENFORCER",
            "Upstream, downstream, nonmembers; enforcing actor and coercive limits.",
        ),
        (360, 260, "CONSEQUENCE", "Water access, payment burden and who bears residual harm."),
    )
    for x, top, title, detail in cells:
        line(c, x, top, x + 160, top, BLACK, 1)
        prose(c, title, (x, top - 8, 160, 14), size=9, color=RED)
        prose(c, detail, (x, top - 28, 160, 48), size=10, font="BF-Serif")
    record_arrow(c, 260, 354, 310, 330)
    record_arrow(c, 440, 354, 390, 330)
    line(c, 250, 330, 450, 330, RED, 1.2)
    prose(c, "PROPOSED ACT d / TIME", (250, 322, 200, 15), size=10, color=RED)
    prose(
        c, "Water levy: period, reasons and scope.", (250, 302, 200, 25), size=10, font="BF-Serif"
    )
    record_arrow(c, 310, 277, 260, 263)
    record_arrow(c, 390, 277, 440, 263)
    record_arrow(c, 260, 182, 310, 163)
    record_arrow(c, 440, 182, 390, 163)
    line(c, 180, 163, 520, 163, RED, 1)
    prose(c, "FUNDED CHALLENGE / INTERIM PROVISION", (180, 155, 340, 15), size=10, color=RED)
    prose(
        c,
        """Maintain essential water. Name reviewer, deadline and binding remedy.
Allow challenge to the forum itself.""",
        (180, 133, 340, 40),
        size=11,
        font="BF-Serif",
    )
    arrow(c, (180, 97), (170, 97))
    arrow(c, (170, 97), (170, 342), dashed=True)
    arrow(c, (170, 342), (350, 342), dashed=True)
    arrow(c, (350, 342), (350, 331))
    prose(c, "REVISION: act, warrant or forum", (180, 82, 340, 15), size=10, color=RED)
    prose(
        c,
        "Red dashed feedback = revision; black arrows = record relationships.",
        (180, 62, 340, 22),
        size=9,
    )
    footer(
        c,
        """Accountability map: classification, competence, reach, enforcement and remedy.
Art: Jerusalem I, plate 55, Library of Congress, c.1832?; uncropped.""",
    )


def draw_evidence(c: Canvas, source: IlluminatedSources) -> None:
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
        f"FINITE INTERVENTIONS / {len(experiment.catalog)} available operators",
        (20, 126, 500, 16),
        size=10,
        color=RED,
    )
    rows = [row for row in experiment.decisions if row.baseline_failed_rules]
    for index, row in enumerate(rows):
        x = 20 + index * 100
        name = row.decision_id.split("-")[0]
        minimum = "N/A" if row.minimum_cardinality is None else str(row.minimum_cardinality)
        prose(c, f"{name} · minimum {minimum}", (x, 104, 96, 25), size=10, font="BF-Serif-Bold")
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
