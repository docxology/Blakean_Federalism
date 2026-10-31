# Copyright (c) 2026 Daniel Ari Friedman
"""Source analysis/search commands and their private-output boundary."""

from pathlib import Path
from typing import Annotated, Final

import typer
from pydantic import TypeAdapter

from .corpus import concordance, load_import
from .corpus_statistics import analyze_corpus
from .models import CorpusPin, Plane, QuerySpec, ResearchError, Role
from .search import search_corpus
from .search_models import SearchRequest
from .search_study import build_search_study
from .search_workspace import build_search_workspace
from .storage import write_new

DEFAULT_PIN: Final = Path("research/corpus-pin.json")
DEFAULT_QUERIES: Final = Path("research/queries.json")
DEFAULT_CORPUS: Final = Path("local_data/corpus/blake-v0.2.0-qualified")


def require_ignored(path: Path, directory: str) -> None:
    if not path.resolve().is_relative_to((Path.cwd() / directory).resolve()):
        raise ResearchError("private_output_required", directory)


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


def search_corpus_command(  # noqa: PLR0913 -- preserve explicit original CLI options
    term: Annotated[
        list[str], typer.Option("--term", help="Literal word or phrase; repeat for alternatives")
    ],
    output: Annotated[Path, typer.Option(help="New ignored source-bound result JSON")],
    *,
    corpus: Path = DEFAULT_CORPUS,
    pin: Path = DEFAULT_PIN,
    mode: str = "any",
    window_words: Annotated[
        int | None, typer.Option(help="ALL-term window of 1-200 original word tokens")
    ] = None,
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
            "window_words": window_words,
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


def register_analysis_commands(app: typer.Typer) -> None:
    """Keep the four original source-analysis/search commands in their original order."""
    _ = app.command()(analyze)
    _ = app.command("search-corpus")(search_corpus_command)
    _ = app.command("build-search-workspace")(build_search_workspace_command)
    _ = app.command("search-study")(search_study_command)
