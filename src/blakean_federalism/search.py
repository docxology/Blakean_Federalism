# Copyright (c) 2026 Daniel Ari Friedman
"""Historical search entry points delegated to the shared literal engine."""

from blake.methods.search import (
    literal_spans as _spans,
)
from blake.methods.search import (
    matching_spans,
    search_corpus,
    search_passages,
)

__all__ = ["_spans", "matching_spans", "search_corpus", "search_passages"]
