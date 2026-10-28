# Copyright (c) 2026 Daniel Ari Friedman
"""Federalism interpretation policy over shared projection custody and retrieval."""

from pathlib import Path

from blake.methods.concordance import concordance as shared_concordance
from blake.methods.concordance import query_fingerprint
from blake.methods.corpus import (
    import_corpus,
    load_import,
    read_passages,
)

from .models import Concordance, CorpusPin, QuerySpec

INTERPRETATION = (
    "Whole-word explicit variants; source-document counts retain copy repetition. "
    "XML includes markup/apparatus. Mixed Erdman pages are not promoted to primary authorship. "
    "Occurrences are retrieval leads, not readings, unique works, or political entailments."
)


def concordance(
    directory: Path,
    queries: tuple[QuerySpec, ...],
    expected_pin: CorpusPin,
) -> Concordance:
    """Keep the paper's historical schema, spans, query hash and interpretation ceiling."""
    result = shared_concordance(directory, queries, expected_pin, INTERPRETATION)
    return Concordance.model_validate(result.model_dump())


__all__ = ["concordance", "import_corpus", "load_import", "query_fingerprint", "read_passages"]
