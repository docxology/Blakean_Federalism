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

from .cli_analysis import (
    DEFAULT_CORPUS,
    DEFAULT_PIN,
    corpus_statistics_command,
    register_analysis_commands,
    require_ignored,
)
from .cli_evidence_review import register_review_commands
from .cli_proximity import proximity_study_command
from .cli_review_comparison import compare_review_command
from .corpus import import_corpus
from .institutional_experiments import run_experiment
from .institutions import assess
from .models import (
    Assessment,
    Concordance,
    CorpusPin,
    CountRow,
    Decision,
    ResearchError,
)
from .report import build_workbench, publish_workbench
from .review_planning_cli import register_review_planning_commands
from .storage import write_new

DEFAULT_CASES: Final = Path("research/cases.json")
DEFAULT_CONCORDANCE: Final = Path("analysis_output/concordance-v0.3.0.json")

app = typer.Typer(no_args_is_help=True)
register_review_commands(app)
_ = app.command("proximity-study")(proximity_study_command)
_ = app.command("compare-review")(compare_review_command)


@app.command("import-corpus")
def import_command(
    source: Annotated[Path, typer.Option(help="Upstream Blake blake_data directory")],
    destination: Annotated[Path, typer.Option(help="New ignored independent projection directory")],
    pin: Path = DEFAULT_PIN,
) -> None:
    require_ignored(destination, "local_data")
    receipt = import_corpus(source, destination, CorpusPin.model_validate_json(pin.read_bytes()))
    typer.echo(receipt.model_dump_json(indent=2))


register_analysis_commands(app)


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


_ = app.command("corpus-statistics")(corpus_statistics_command)


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
    readings: str = "research/scholarship-reading-0.13.0.json",
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
    readings: str = "research/scholarship-reading-0.13.0.json",
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


register_review_planning_commands(app)


if __name__ == "__main__":
    app()
