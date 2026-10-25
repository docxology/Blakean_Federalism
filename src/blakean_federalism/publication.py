# Copyright (c) 2026 Daniel Ari Friedman
"Prepare a new source-bound manuscript stage for the pinned external template."

import json
from pathlib import Path

from . import __version__
from .manuscript import ManuscriptSpec, validate_manuscript
from .models import ResearchError
from .publication_contract import manuscript_contract, source_bindings
from .publication_figures import generate_figures
from .publication_models import PreparedPublication, TemplateRendering
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
    contract = manuscript_contract(
        article + "\n\n" + appendix, safe_path(root, SOURCE_NAMES[2]).read_text()
    )
    variables = manuscript_variables(report)
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ResearchError("occupied_output", str(output)) from exc
    raw = output / "manuscript"
    raw.mkdir()
    figures = output / "output/figures"
    generated = generate_figures(report, figures, rasterizer)
    for name in SOURCE_NAMES[:5]:
        copy_new(safe_path(root, name), raw / Path(name).name)
    front: list[str] = [
        "```{=html}",
        "<style>",
        "html {color-scheme: light;}",
        "a:any-link:not(.skip-link) {color: #235f5a;}",
        ".table-scroll > table {table-layout: fixed; width: 100%; min-width: 100%;}",
        ".table-scroll col {width: auto !important;}",
        "th, td {white-space: normal; overflow-wrap: anywhere;}",
        ".figure-full-size-link {left: auto; transform: none; width: 100%; max-width: 100%;}",
        "mjx-container[display] {max-width: 100%; overflow-x: auto;}",
        ".graphical-cover img {width: 100%; height: auto;}",
        "</style>",
        '<figure class="graphical-cover" id="graphical-cover">',
        '<a href="../figures/abstract-1.png" aria-label="Open cover abstract at full size">',
        (
            '<img src="../figures/abstract-1.png" alt="Interwoven national formations, '
            'plural affiliations and recurring poetic-state interpretations." /></a>'
        ),
        "<figcaption>Composition without capture.</figcaption></figure>",
        "```",
        "",
        r"\setcounter{page}{2}",
        r"\thispagestyle{plain}",
        "",
    ]
    titles = (
        "From passage to public reasons",
        "Anatomy of a public decision",
        "Agreement and the freedom to dissent",
    )
    descriptions = (
        (
            "Close reading identifies a passage and its context. Reconstruction develops "
            "the political distinction. Institutional comparison specifies powers, "
            "costs and review."
        ),
        (
            "A proposed water levy separates the issuing body, its competence, affected reach "
            "and enforcement. Reasons, standing and review make each claim answerable."
        ),
        (
            "Agreement can emerge through translation and revision or through dependence and "
            "gatekeeping. The comparison asks what it costs to challenge the shared decision."
        ),
    )
    for number, title in enumerate(titles, start=2):
        front.extend(
            [
                f"# Graphical abstract {number}: {title} {{.unnumbered .unlisted}}",
                "",
                (
                    "![Project-authored graphical abstract; the argument and sources "
                    "are developed in the article.]"
                    f"(../figures/abstract-{number}.png){{#fig:abstract-{number} width=98%}}"
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
        "# Critical plate atlas {#sec:atlas}",
        "",
        ("Copies, dates, source transcriptions and rights are distinct evidence objects."),
        "",
    ]
    for asset in report.images:
        source = assets[asset.asset_id]
        target = figures / ("plate-" + asset.asset_id + source.suffix)
        copy_new(source, target)
        atlas.extend(
            [
                f"## {asset.asset_id}: selected impression",
                "",
                (
                    f"![{asset.caption}](../figures/{target.name})"
                    f"{{#fig:plate-{asset.asset_id} height=5.5in}}"
                ),
                "",
                f"Credit: {asset.credit}. {asset.rights_basis}. [Item rights]({asset.rights_url}).",
                "",
                (
                    "Uncropped historical impression, proportionally scaled. "
                    "The passage transcription is identified separately in the article."
                ),
                "",
                r"\clearpage",
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
