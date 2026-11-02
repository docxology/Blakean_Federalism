# Copyright (c) 2026 Daniel Ari Friedman
"""Bind delegated public methods separately from unchanged historical measurements."""

from blake.methods.producer import SourceBinding, source_hashes

SHARED_SOURCES = (
    "__init__.py",
    "version.py",
    "methods/__init__.py",
    "methods/common.py",
    "methods/intervals.py",
    "methods/models.py",
    "methods/projection_models.py",
    "methods/bundle_models.py",
    "methods/profiles.py",
    "methods/storage.py",
    "methods/corpus.py",
    "methods/concordance.py",
    "methods/statistics.py",
    "methods/statistics_core.py",
    "methods/statistics_models.py",
    "methods/search.py",
    "methods/search_models.py",
    "methods/search_study.py",
    "methods/proximity.py",
    "methods/producer.py",
    "methods/runs.py",
)


def shared_source_hashes() -> dict[str, str]:
    """Expose the actual shared source closure in newly produced application receipts."""
    return source_hashes((SourceBinding("blake", SHARED_SOURCES),))
