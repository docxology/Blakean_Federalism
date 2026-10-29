# Copyright (c) 2026 Daniel Ari Friedman
"""Application-selected comparisons delegated to shared literal methods."""

from blake.methods.models import ProjectionCorpusPin as CorpusPin
from blake.methods.models import ProjectionPassage as Passage
from blake.methods.search_study import SearchStudy, StudyQuery
from blake.methods.search_study import build_search_study as _build


def build_search_study(passages: tuple[Passage, ...], pin: CorpusPin) -> SearchStudy:
    """Retain this study's selected queries and their exact ordering."""
    selected = (
        ("minute_particulars", ("minute particulars",)),
        ("general_forms", ("general forms",)),
        ("liberty", ("liberty",)),
        ("freedom", ("freedom",)),
        ("brotherhood", ("brotherhood",)),
        ("nation", ("nation",)),
        ("negative_control", ("zzzxqvnegativecontrol",)),
    )
    return _build(passages, pin, selected)


__all__ = ["SearchStudy", "StudyQuery", "build_search_study"]
