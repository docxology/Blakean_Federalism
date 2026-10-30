# Copyright (c) 2026 Daniel Ari Friedman
"""Prepare the graphical opening without coupling it to corpus and artifact custody."""

from pathlib import Path

from .abstract_captions import analytical_captions, cover_caption, uses_analytical_abstracts
from .models import ResearchError
from .storage import write_new
from .workbench_models import Workbench


def _abstract_captions(report: Workbench) -> tuple[str, str, str]:
    if uses_analytical_abstracts(report):
        return analytical_captions(report)[1:]
    observed = report.corpus_statistics
    experiment = report.institutional_experiments
    if observed is None or experiment is None:
        raise ResearchError(
            "publication_statistics", "Abstract requires observed and synthetic data"
        )
    failed_count = sum(bool(row.baseline_failed_rules) for row in experiment.decisions)
    art = any(asset.asset_id == "J1" for asset in report.images)
    return (
        "".join(
            (
                "Jerusalem 52 accompanies " if art else "",
                "three rows connecting person/state distinction, collective interpretation and ",
                "contestable review. Each aligns a Blake passage, two scholarly readings and ",
                "the institutional question their disagreement makes necessary.",
            )
        ),
        "".join(
            (
                "Jerusalem 55 accompanies " if art else "",
                "one hypothetical water levy. Entity/role and issuer/warrant ",
                "enter the proposed act; ",
                "reach/enforcement and consequence describe its effects. ",
                "Funded challenge and interim ",
                "water provision return revision to the act, its warrant or its reviewing forum.",
            )
        ),
        "".join(
            (
                "Jerusalem 91 frames " if art else "",
                "eight lexical comparisons: occurrences, unit/family coverage ",
                "and pooled/equal-family ",
                f"rates ({observed.primary_source_units} primary extracts; ",
                f"{observed.primary_work_groups} families; {observed.primary_tokens:,} tokens). ",
                f"Below, {failed_count} failed baselines give minimum changes among ",
                f"{len(experiment.catalog)} interventions. ",
                f"All {len(experiment.decisions)} alternatives ",
                f"produce {experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                f"admissible subsets and {experiment.total_distinct_states} distinct records.",
            )
        ),
    )


def _abstract_labels(*, current: bool) -> tuple[tuple[str, str, str], tuple[str, str, str]]:
    if current:
        return (
            (
                "Blake's scenes and institutional questions",
                "Comparing repairs in five conflicts",
                ("Counting words in their sources"),
            ),
            ("", "", ""),
        )
    return (
        (
            "Disagreement changes the institutional design",
            ("A water levy from classification to effective review"),
            ("Observed text and finite safeguard comparisons"),
        ),
        (
            (
                "Read each row from "
                "passage through "
                "scholarly "
                "disagreement to "
                "institutional "
                "question."
            ),
            ("Read the two inputs into the act, then its effects and the routes for revision."),
            ("Compare source weighting above and finite intervention sets below."),
        ),
    )


def write_graphical_abstracts(raw: Path, report: Workbench, *, full_artwork: bool) -> None:
    """Preserve the source-derived graphical opening for the selected visual profile."""
    front: list[str] = [
        "```{=html}",
        '<script>window.MathJax.output.displayOverflow = "scroll";</script>',
        "<style>",
        "html {color-scheme: light;}",
        "blockquote {font-style:italic !important; border-left:3px solid #b00020;",
        "margin:1rem 0; padding:0.2rem 0 0.2rem 1.2rem; line-height:1.5;}",
        "blockquote p {margin:0;}",
        "figure {margin-block:1.7rem 2rem;}",
        "figcaption {font-size:0.9rem; line-height:1.45; text-align:left;",
        "font-style:normal; margin-top:0.6rem; padding-top:0.5rem;",
        "border-top:1px solid #ccc; color:#000 !important;}",
        "h2, h3, h4 {line-height:1.25;}",
        "p {orphans:3; widows:3;}",
        "a:any-link, a:any-link *, #TOC a:any-link {color: #b00020 !important;}",
        "h1, h2, h3, h4, h5, h6 {color: #000 !important; border-color: #b00020 !important;}",
        "html, body, main, article {color: #000 !important; background: #fff !important;}",
        ":root {--brand-1:#b00020 !important; --web-bg:#fff !important;",
        "--web-surface:#fff !important; --web-text:#000 !important;",
        "--web-border:#ccc !important;}",
        "th, pre, code {background:#f2f2f2 !important; color:#000 !important;}",
        ".toc, #TOC {background:#f2f2f2 !important; border-color:#ccc !important;}",
        ".skip-link {background:#fff !important;}",
        "img, .figure img {border-color:#ccc !important;}",
        "*:focus-visible {outline-color:#b00020 !important;}",
        ".table-scroll > table {table-layout: fixed; width: 100%; min-width: 100%;}",
        ".table-scroll col {width: auto !important;}",
        "th, td {white-space: normal; overflow-wrap: anywhere;}",
        ".figure-full-size-link {left: auto; transform: none; width: 100%; max-width: 100%;}",
        "mjx-container[display] {max-width: 100%; overflow-x: auto;}",
        ".graphical-cover img {width: 100%; height: auto;}",
        "figure img {height: auto !important;}",
        "</style>",
        '<figure class="graphical-cover" id="graphical-cover">',
        '<a href="../figures/abstract-1.png" aria-label="Open cover abstract at full size">',
        (
            '<img src="../figures/abstract-1.png" alt="Jerusalem frontispiece, '
            "italic quotations, national formations, "
            'plural affiliations and recurring poetic-state interpretations." /></a>'
        ),
        (
            "<figcaption>"
            + (
                cover_caption()
                if uses_analytical_abstracts(report)
                else "Composition without capture. "
                + (
                    """Jerusalem I, frontispiece; LOC item 48038103, posthumous impression,
approximately 1832?. Original plate beside the article's distinct affiliation,
interpretation and competence relations."""
                    if full_artwork
                    else "Affiliation, interpretation and claimed competence."
                )
            )
            + "</figcaption></figure>"
        ),
        "```",
        "",
        r"\setcounter{page}{2}",
        r"\thispagestyle{plain}",
        "",
    ]
    titles, descriptions = _abstract_labels(current=uses_analytical_abstracts(report))
    captions = _abstract_captions(report)
    for number, title in enumerate(titles, start=2):
        width = 92 if number == len(titles) + 1 else 98
        front.extend(
            [
                f"# Graphical abstract {number}: {title} {{.unnumbered .unlisted}}",
                "",
                (
                    "".join(
                        (
                            f"![{captions[number - 2]}]",
                            f"(../figures/abstract-{number}.png)",
                            f"{{#fig:abstract-{number} width={width}%}}",
                        )
                    )
                ),
                "",
                descriptions[number - 2],
                "",
                r"\clearpage",
                "",
            ]
        )
    front.extend([r"\BFcontents", "", r"\clearpage", ""])
    write_new(raw / "00_graphical_abstracts.md", "\n".join(front))
