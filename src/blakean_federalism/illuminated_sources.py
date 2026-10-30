# Copyright (c) 2026 Daniel Ari Friedman
"""Immutable source bundle consumed by the illuminated reading and record figures."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .corpus_statistics_models import CorpusStatistics
from .institutional_experiment_models import InstitutionalExperiment
from .manuscript import Quotation
from .workbench_models import Workbench


@dataclass(frozen=True, slots=True)
class IlluminatedSources:
    report: Workbench
    artwork: Mapping[str, Path]
    quotations: Mapping[str, Quotation]
    statistics: CorpusStatistics
    experiment: InstitutionalExperiment

    def verse(self, quote_id: str, start: int = 0, stop: int | None = None) -> str:
        return " ".join(s.text for s in self.quotations[quote_id].segments[start:stop])
