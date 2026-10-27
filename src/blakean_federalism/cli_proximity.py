# Copyright (c) 2026 Daniel Ari Friedman
"""Export the fixed primary-corpus proximity comparison without source contexts."""

from pathlib import Path
from typing import Annotated, Final

import typer

from .models import CorpusPin
from .proximity_study import produce_proximity_study
from .search_study import SearchStudy
from .storage import write_new

DEFAULT_CORPUS: Final = Path("local_data/corpus/blake-v0.2.0-qualified")
DEFAULT_PIN: Final = Path("research/corpus-pin.json")
DEFAULT_RETAINED: Final = Path("research/search-study-0.8.0.json")


def proximity_study_command(
    output: Annotated[Path, typer.Option(help="New aggregate-only proximity JSON")],
    corpus: Path = DEFAULT_CORPUS,
    pin: Path = DEFAULT_PIN,
    retained: Path = DEFAULT_RETAINED,
) -> None:
    """Compare six primary-text pairs at four word budgets and document-wide ALL."""
    expected = CorpusPin.model_validate_json(pin.read_bytes())
    historical = SearchStudy.model_validate_json(retained.read_bytes())
    result = produce_proximity_study(corpus, expected, historical)
    write_new(output, result.model_dump_json(indent=2) + "\n")
    typer.echo(f"{result.scanned_source_units} scanned units; {len(result.rows)} aggregate rows")
