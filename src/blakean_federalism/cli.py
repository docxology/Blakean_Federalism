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

from .corpus import concordance, import_corpus
from .institutions import assess
from .models import Assessment, Concordance, CorpusPin, CountRow, Decision, QuerySpec, ResearchError
from .report import build_workbench, publish_workbench
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
    typer.echo("Retrieval leads only; no semantic, absence-across-oeuvre or legitimacy inference.")


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
    typer.echo(f"{len(assessments)} stipulated cases assessed; no empirical or legal verdict.")


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
    readings: str = "research/scholarship-reading-0.4.1.json",
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
    readings: str = "research/scholarship-reading-0.4.1.json",
) -> None:
    "Hydrate and render with docxology/template; content checks do not imply visual acceptance."
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
