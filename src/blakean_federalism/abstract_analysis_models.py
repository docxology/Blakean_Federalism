# Copyright (c) 2026 Daniel Ari Friedman
"""Text-free descriptive records for graphical abstract data."""

from .institutional_experiment_models import Intervention
from .models import FrozenModel


class QueryDiagnostic(FrozenModel):
    query_id: str
    source_units: int
    tokens: int
    occurrences: int
    matched_units: int
    positive_token_families: int
    matched_families: int
    pooled_rate: float | None
    equal_family_rate: float | None
    top_family_ids: tuple[str, ...]
    top_family_occurrences: int
    top_family_share: float | None
    loo_min_rate: float | None
    loo_min_family_ids: tuple[str, ...]
    loo_max_rate: float | None
    loo_max_family_ids: tuple[str, ...]


class RepairCase(FrozenModel):
    decision_id: str
    baseline_failed_rules: tuple[str, ...]
    minimal_bundles: tuple[tuple[Intervention, ...], ...]
    essential_interventions: tuple[Intervention, ...]
    minimum_cardinality: int | None
    subset_count: int
    admissible_subsets: int
    distinct_states: int
    admissible_by_size: tuple[int, ...]
    admission_fraction: float
    unique_minimal_bundle: bool


class RepairPartition(FrozenModel):
    decisions: int
    subset_count: int
    admissible_subsets: int
    distinct_states: int
    admission_fraction: float | None


class RepairDiagnostics(FrozenModel):
    cases: tuple[RepairCase, ...]
    baseline_admissible: RepairPartition
    baseline_failing: RepairPartition
    total_subsets: int
    total_admissible_subsets: int
    total_distinct_states: int
