# Copyright (c) 2026 Daniel Ari Friedman
"Finite local research commands; full texts and concordances remain ignored."

import csv
import io
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Annotated, Final

import typer
from pydantic import TypeAdapter

from .corpus import concordance, import_corpus, load_import
from .corpus_statistics import analyze_corpus
from .institutional_experiments import run_experiment
from .institutions import assess
from .models import (
    Assessment,
    Concordance,
    CorpusPin,
    CountRow,
    Decision,
    Plane,
    QuerySpec,
    ResearchError,
    Role,
)
from .report import build_workbench, publish_workbench
from .search import search_corpus
from .search_models import SearchRequest
from .search_study import build_search_study
from .search_workspace import build_search_workspace
from .storage import write_new

DEFAULT_PIN: Final = Path("research/corpus-pin.json")
DEFAULT_QUERIES: Final = Path("research/queries.json")
DEFAULT_CASES: Final = Path("research/cases.json")
DEFAULT_CORPUS: Final = Path("local_data/corpus/blake-v0.2.0-qualified")
DEFAULT_CONCORDANCE: Final = Path("analysis_output/concordance-v0.3.0.json")

app = typer.Typer(no_args_is_help=True)


def require_ignored(path: Path, directory: str) -> None:
    if not path.resolve().is_relative_to((Path.cwd() / directory).resolve()):
        raise ResearchError("private_output_required", directory)


@app.command("import-corpus")
def import_command(
    source: Annotated[Path, typer.Option(help="Upstream Blake blake_data directory")],
    destination: Annotated[Path, typer.Option(help="New ignored independent projection directory")],
    pin: Path = DEFAULT_PIN,
) -> None:
    require_ignored(destination, "local_data")
    receipt = import_corpus(source, destination, CorpusPin.model_validate_json(pin.read_bytes()))
    typer.echo(receipt.model_dump_json(indent=2))


@app.command()
def analyze(
    corpus: Annotated[Path, typer.Option(help="Previously verified independent projection")],
    output: Annotated[Path, typer.Option(help="New ignored JSON concordance path")],
    queries: Path = DEFAULT_QUERIES,
    pin: Path = DEFAULT_PIN,
) -> None:
    require_ignored(output, "analysis_output")
    specs = TypeAdapter(tuple[QuerySpec, ...]).validate_json(queries.read_bytes())
    result = concordance(corpus, specs, CorpusPin.model_validate_json(pin.read_bytes()))
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(
        f"{result.scanned_source_documents} source documents; {len(result.hits)} occurrences"
    )
    typer.echo("Saved spans, source roles and editions support close reading.")


@app.command("search-corpus")
def search_corpus_command(
    term: Annotated[
        list[str], typer.Option("--term", help="Literal word or phrase; repeat for alternatives")
    ],
    output: Annotated[Path, typer.Option(help="New ignored source-bound result JSON")],
    *,
    corpus: Path = DEFAULT_CORPUS,
    pin: Path = DEFAULT_PIN,
    mode: str = "any",
    role: Role | None = None,
    plane: Plane | None = None,
    work_id: str | None = None,
    all_sources: bool = False,
    substring: bool = False,
    limit: int = 100,
    context_chars: int = 120,
) -> None:
    """Search literal Unicode text across the verified corpus, independently of saved queries."""
    require_ignored(output, "analysis_output")
    if all_sources and role is not None:
        raise ResearchError("search_role", "Choose --all-sources or --role")
    request = SearchRequest.model_validate(
        {
            "terms": tuple(term),
            "mode": mode,
            "role": None if all_sources else (role or Role.PRIMARY),
            "plane": plane,
            "work_id": work_id,
            "whole_words": not substring,
            "limit": limit,
            "context_chars": context_chars,
        }
    )
    result = search_corpus(corpus, CorpusPin.model_validate_json(pin.read_bytes()), request)
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(
        "".join(
            (
                f"{result.total_occurrences} occurrences; ",
                f"{result.matched_source_units}/{result.eligible_source_units} eligible units; ",
                f"{result.returned_hits} returned",
            )
        )
    )


@app.command("build-search-workspace")
def build_search_workspace_command(
    output: Annotated[
        Path, typer.Option(help="New ignored directory containing local full-text search")
    ],
    corpus: Path = DEFAULT_CORPUS,
    pin: Path = DEFAULT_PIN,
) -> None:
    """Build a standalone offline full-text workspace; keep this artifact local."""
    require_ignored(output, "analysis_output")
    typer.echo(
        str(build_search_workspace(corpus, CorpusPin.model_validate_json(pin.read_bytes()), output))
    )


@app.command("search-study")
def search_study_command(
    output: Annotated[Path, typer.Option(help="New aggregate-only search study JSON")],
    corpus: Path = DEFAULT_CORPUS,
    pin: Path = DEFAULT_PIN,
) -> None:
    """Compare seven literal searches across every imported source role."""
    expected = CorpusPin.model_validate_json(pin.read_bytes())
    _, passages = load_import(corpus, expected)
    result = build_search_study(passages, expected)
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(f"{result.source_units} source units; {len(result.queries)} literal queries")


@app.command("assess-cases")
def assess_cases(
    output: Annotated[Path, typer.Option(help="New generated assessment file")],
    cases: Path = DEFAULT_CASES,
) -> None:
    require_ignored(output, "analysis_output")
    records = TypeAdapter(tuple[Decision, ...]).validate_json(cases.read_bytes())
    if len({r.decision_id for r in records}) != len(records):
        raise ResearchError("duplicate_decision", str(cases))
    assessments = tuple(assess(r) for r in records)
    write_new(
        output, TypeAdapter(tuple[Assessment, ...]).dump_json(assessments, indent=2).decode() + "\n"
    )
    typer.echo(f"{len(assessments)} synthetic records assessed; every safeguard check retained.")


@app.command("corpus-statistics")
def corpus_statistics_command(
    output: Annotated[Path, typer.Option(help="New ignored statistics JSON path")],
    corpus: Path = DEFAULT_CORPUS,
    queries: Path = DEFAULT_QUERIES,
    pin: Path = DEFAULT_PIN,
) -> None:
    """Compare copy-retaining, exact-text and equal-family primary corpus measures."""
    require_ignored(output, "analysis_output")
    _, passages = load_import(corpus, CorpusPin.model_validate_json(pin.read_bytes()))
    specs = TypeAdapter(tuple[QuerySpec, ...]).validate_json(queries.read_bytes())
    result = analyze_corpus(passages, specs)
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(
        "".join(
            (
                f"{result.primary_source_units} primary units; {result.primary_work_groups} ",
                f"source families; {result.primary_tokens} tokens",
            )
        )
    )


@app.command("experiment-cases")
def experiment_cases_command(
    output: Annotated[Path, typer.Option(help="New ignored finite-experiment JSON path")],
    cases: Path = DEFAULT_CASES,
) -> None:
    """Enumerate declared safeguard changes while preserving material conditions."""
    require_ignored(output, "analysis_output")
    records = TypeAdapter(tuple[Decision, ...]).validate_json(cases.read_bytes())
    result = run_experiment(records)
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(
        "".join(
            (
                f"{result.total_subsets} subsets; {result.total_distinct_states} ",
                "distinct resulting records",
            )
        )
    )


@app.command("export-schemas")
def export_schemas(output: Annotated[Path, typer.Option(help="New schema JSON file")]) -> None:
    write_new(output, json.dumps(Decision.model_json_schema(), indent=2) + "\n")


@app.command("export-summary")
def export_summary(
    concordance_file: Annotated[Path, typer.Option(help="Private concordance JSON")],
    output: Annotated[Path, typer.Option(help="New aggregate-only CSV path")],
) -> None:
    "Export only plane/role/count fields; source contexts and quotations cannot enter the CSV."
    result = Concordance.model_validate_json(concordance_file.read_bytes())
    buffer = io.StringIO(newline="")
    fields = list(CountRow.model_fields)
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    writer.writerows(row.model_dump(mode="json") for row in result.rows)
    write_new(output, buffer.getvalue())
    typer.echo(f"{len(result.rows)} aggregate count rows exported; no source contexts.")


@app.command("build-workbench")
def build_workbench_command(
    corpus: Annotated[Path, typer.Option(help="Verified independent local projection")],
    concordance_file: Annotated[Path, typer.Option(help="Private source-bound concordance JSON")],
    output: Annotated[Path, typer.Option(help="New ignored workbench directory")],
    readings: str = "research/scholarship-reading-0.9.0.json",
) -> None:
    require_ignored(output, "analysis_output")
    report = build_workbench(Path.cwd(), corpus, concordance_file, readings)
    typer.echo(str(publish_workbench(report, output)))


@app.command("render-manuscript")
def render_manuscript_command(
    template_root: Annotated[
        Path, typer.Option(help="Clean checkout at the declared template commit")
    ],
    template_python: Annotated[
        Path, typer.Option(help="External compatible template environment Python")
    ],
    output: Annotated[Path, typer.Option(help="New ignored publication stage")],
    corpus: Path = DEFAULT_CORPUS,
    concordance_file: Path = DEFAULT_CONCORDANCE,
    readings: str = "research/scholarship-reading-0.9.0.json",
) -> None:
    "Hydrate with docxology/template and verify references, sources and quotations."
    # Optional manuscript dependencies must not become core CLI import requirements.
    from .publication import prepare_publication  # noqa: PLC0415
    from .publication_verification import verify_publication  # noqa: PLC0415

    require_ignored(output, "analysis_output")
    root = Path.cwd()
    worker = root / "tools/template_render.py"
    uv = shutil.which("uv")
    rasterizer = shutil.which("pdftoppm")
    if uv is None or rasterizer is None or not worker.is_file():
        raise ResearchError(
            "publication_tools", "Require uv, pdftoppm and the project source checkout"
        )
    report = build_workbench(root, corpus, concordance_file, readings)
    stage = prepare_publication(root, output, report, rasterizer)
    environment = dict(os.environ)
    _ = environment.pop("VIRTUAL_ENV", None)
    environment["UV_PROJECT_ENVIRONMENT"] = str(template_python.absolute().parent.parent)
    with (stage / "native-render.log").open("x") as log:
        result = subprocess.run(  # noqa: S603 -- Explicit argv; selected source/runtime, no shell.
            [
                uv,
                "run",
                "--no-sync",
                "--offline",
                "--project",
                str(template_root),
                "--python",
                str(template_python),
                "python",
                str(worker),
                "--template-root",
                str(template_root),
                "--stage",
                str(stage),
            ],
            stdout=log,
            stderr=subprocess.STDOUT,
            env=environment,
            check=False,
        )
    if result.returncode:
        raise ResearchError("template_render_failed", str(stage / "native-render.log"))
    typer.echo(json.dumps(verify_publication(root, stage), indent=2))


if __name__ == "__main__":
    app()
