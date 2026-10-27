# Copyright (c) 2026 Daniel Ari Friedman
"Prepare a new source-bound manuscript stage for the pinned external template."

import json
from pathlib import Path

from . import __version__
from .manuscript import ManuscriptSpec, validate_manuscript
from .models import ResearchError
from .proximity_study import ProximityStudy
from .publication_contract import manuscript_contract, source_bindings
from .publication_figures import generate_figures
from .publication_models import PreparedPublication, TemplateRendering
from .search_study import SearchStudy
from .storage import copy_new, digest, safe_path, verify_file, write_new
from .workbench_models import Workbench

SOURCE_NAMES = (
    "docs/manuscript/states-change.md",
    "docs/manuscript/references-and-rights.md",
    "docs/manuscript/references.bib",
    "docs/manuscript/config.yaml",
    "docs/manuscript/preamble.md",
    "research/manuscript-inputs.json",
    "research/template-rendering.json",
    "research/citation-catalog.json",
    "research/search-study-0.8.0.json",
    "docs/manuscript/notation.md",
    "research/proximity-study-0.10.0.json",
)


def manuscript_variables(report: Workbench) -> dict[str, str]:
    census: dict[tuple[str, str], int] = {}
    for cell in report.coverage:
        key = (cell.plane.value, cell.role.value)
        if key in census and census[key] != cell.source_units:
            raise ResearchError("publication_census", "Stratum denominators disagree")
        census[key] = cell.source_units
    if sum(census.values()) != report.source_units:
        raise ResearchError("publication_census", "Source-unit census does not reconcile")
    state = next(
        (
            cell
            for cell in report.coverage
            if cell.query_id == "states"
            and cell.plane.value == "reading"
            and cell.role.value == "primary"
        ),
        None,
    )
    return {
        "STATES_PRIMARY_OCCURRENCES": str(state.occurrences) if state else "N/A",
        "STATES_PRIMARY_MATCHED": str(state.matched_source_documents) if state else "N/A",
        "STATES_PRIMARY_UNITS": str(state.source_units) if state else "N/A",
        "STATES_PRIMARY_PERCENT": f"{100 * state.coverage_fraction:.1f}"
        if state and state.coverage_fraction is not None
        else "N/A",
        "VERSION": __version__,
        "SOURCE_UNITS": f"{report.source_units:,}",
        "OCCURRENCES": f"{report.stored_occurrences:,}",
        "COVERAGE_CELLS": str(len(report.coverage)),
        "CASE_ALTERNATIVES": str(len(report.cases)),
        "CASE_CHECKS": str(sum(len(case.assessment.checks) for case in report.cases)),
        **{f"UNITS_{p.upper()}_{r.upper()}": str(n) for (p, r), n in census.items()},
    }


def _abstract_captions(report: Workbench) -> tuple[str, str, str]:
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
                "Jerusalem 52 and its person/state epigraph accompany " if art else "",
                "three pairs of scholarly arguments framing the design questions: ",
                "what may change, who interprets, and who can challenge the reviewer.",
            )
        ),
        "".join(
            (
                "Jerusalem 55 and its injunction to labor for those in misery accompany "
                if art
                else "",
                "a water levy separating entity and role from issuing authority, affected reach, ",
                "enforcement and consequence. Red feedback paths return challenge and interim ",
                "duties to the decision.",
            )
        ),
        "".join(
            (
                "Jerusalem 91 frames " if art else "",
                "eight lexical comparisons: occurrences, matched/eligible units and families, ",
                "and pooled/equal-family rates ",
                f"({observed.primary_source_units} primary extracts; ",
                f"{observed.primary_work_groups} families; {observed.primary_tokens:,} tokens). ",
                f"{failed_count} failed baselines give ",
                "failed-rule counts, minimum interventions and ",
                f"admissible subsets. Totals cover all {len(experiment.decisions)} alternatives: ",
                f"{experiment.total_admissible_subsets:,}/{experiment.total_subsets:,} ",
                f"admissible subsets, {experiment.total_distinct_states} distinct records.",
            )
        ),
    )


def _publication_studies(root: Path, report: Workbench) -> tuple[SearchStudy, ProximityStudy]:
    historical = SearchStudy.model_validate_json(
        safe_path(root, "research/search-study-0.8.0.json").read_bytes()
    )
    nearby = ProximityStudy.model_validate_json(
        safe_path(root, "research/proximity-study-0.10.0.json").read_bytes()
    )
    observed = report.corpus_statistics
    if (
        historical.corpus_pin != report.corpus_pin
        or nearby.corpus_pin != report.corpus_pin
        or historical.source_units != report.source_units
        or nearby.scanned_source_units != report.source_units
        or observed is None
        or nearby.rows[0].eligible_source_units != observed.primary_source_units
        or nearby.rows[0].eligible_word_tokens != observed.primary_tokens
        or nearby.rows[0].eligible_source_families != observed.primary_work_groups
    ):
        raise ResearchError("search_study_pin", "Search studies must match the publication corpus")
    return historical, nearby


def prepare_publication(root: Path, output: Path, report: Workbench, rasterizer: str) -> Path:
    """Validate before reserving a stage; never reuse another run's output tree."""
    root = root.absolute()
    output = output.absolute()
    if ".." in output.parts or not output.is_relative_to(root / "analysis_output"):
        raise ResearchError("publication_output", "Require a new analysis_output descendant")
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ResearchError("symlink_output", str(output))
    producers = tuple(
        sorted(
            p.relative_to(root).as_posix()
            for p in (root / "src/blakean_federalism").rglob("*")
            if p.is_file() and p.suffix in (".py", ".css", ".js", ".html", ".ttf", ".txt")
        )
    )
    before = source_bindings(root, SOURCE_NAMES + producers + ("tools/template_render.py",))
    for binding in report.inputs:
        _ = verify_file(root, binding.path, binding.size, binding.sha256)
    article = safe_path(root, SOURCE_NAMES[0]).read_text()
    appendix = safe_path(root, SOURCE_NAMES[1]).read_text()
    spec = ManuscriptSpec.model_validate_json(safe_path(root, SOURCE_NAMES[5]).read_bytes())
    assets = validate_manuscript(root, spec, article + "\n\n" + appendix)
    notation = safe_path(root, "docs/manuscript/notation.md").read_text()
    contract = manuscript_contract(
        notation + "\n\n" + article + "\n\n" + appendix,
        safe_path(root, SOURCE_NAMES[2]).read_text(),
    )
    variables = manuscript_variables(report)
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ResearchError("occupied_output", str(output)) from exc
    raw = output / "manuscript"
    raw.mkdir()
    figures = output / "output/figures"
    search_study, proximity_study = _publication_studies(root, report)
    generated = generate_figures(
        report,
        figures,
        rasterizer,
        search_study,
        proximity_study,
        artwork=assets if spec.version == "0.11.0" else None,
    )
    for name in SOURCE_NAMES[:5]:
        copy_new(safe_path(root, name), raw / Path(name).name)
    write_new(raw / "01_notation.md", notation + "\n\n" + r"\clearpage" + "\n")
    front: list[str] = [
        "```{=html}",
        '<script>window.MathJax.output.displayOverflow = "scroll";</script>',
        "<style>",
        "html {color-scheme: light;}",
        "blockquote {font-style:italic !important; border-left:3px solid #b00020;}",
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
            "<figcaption>Composition without capture. "
            + (
                """Jerusalem I, frontispiece; LOC item 48038103, posthumous impression,
approximately 1832?. Original plate beside the article's distinct affiliation,
interpretation and competence relations."""
                if spec.version == "0.11.0"
                else "Affiliation, interpretation and claimed competence."
            )
            + "</figcaption></figure>"
        ),
        "```",
        "",
        r"\setcounter{page}{2}",
        r"\thispagestyle{plain}",
        "",
    ]
    titles = (
        "Disagreement changes the institutional design",
        "A water levy from classification to effective review",
        "Observed text and finite safeguard comparisons",
    )
    descriptions = (
        (
            "Three paired scholarly tensions and proposed tests connect permanence, "
            "reciprocity and protection to "
            "standing, interpretive authority and contestable review."
        ),
        (
            "A branched decision map separates classification, competence, "
            "reach and enforcement, with challenge and interim duties "
            "feeding back into the act."
        ),
        (
            "Eight focus rows give exact occurrence, unit and family coverage, "
            "pooled rates and equal-family means; "
            "minimum intervention counts expose the programmed deficits of five "
            "synthetic capture records."
        ),
    )
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
    atlas: list[str] = [
        r"\clearpage",
        "",
        "# Plate sources and credits {#sec:atlas}",
        "",
        (
            f"{len(report.images)} uncropped LOC reproductions accompany the main-text readings. "
            "The item-attached advisory reports no known U.S. restrictions; it is not a CC0 "
            "license. Each caption identifies the impression separately "
            "from the ASU transcription. "
            f"Credits: {'; '.join(dict.fromkeys(asset.credit for asset in report.images))}."
        ),
        "",
    ]
    for asset in report.images:
        source = assets[asset.asset_id]
        target = figures / ("plate-" + asset.asset_id + source.suffix)
        copy_new(source, target)
        atlas.extend(
            [
                f"**{asset.asset_id}: selected impression.**",
                "",
                " ".join(
                    (
                        asset.caption,
                        f"[Item rights]({asset.rights_url}).",
                    )
                ),
                "",
            ]
        )
    write_new(raw / "90_atlas.md", "\n".join(atlas))
    write_new(output / "manuscript_variables.json", json.dumps(variables, indent=2) + "\n")
    write_new(output / "workbench-data.json", report.model_dump_json(indent=2) + "\n")
    receipt = PreparedPublication(
        producer_version=__version__,
        inputs=before,
        contract=contract,
        template=TemplateRendering.model_validate_json(
            safe_path(root, SOURCE_NAMES[6]).read_bytes()
        ),
        source_order=(
            "00_graphical_abstracts.md",
            "01_notation.md",
            "states-change.md",
            "references-and-rights.md",
            "90_atlas.md",
        ),
        figures={p.name: digest(p) for p in figures.iterdir()},
        generated_schematics=generated,
        variables=variables,
        scope="Prepared stage only; native rendering and visual review are separate gates",
    )
    if before != source_bindings(root, tuple(before)):
        raise ResearchError("publication_source_changed", "Source changed during preparation")
    write_new(output / "prepared-publication.json", receipt.model_dump_json(indent=2) + "\n")
    return output
