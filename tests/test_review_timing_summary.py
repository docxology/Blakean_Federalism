# Copyright (c) 2026 Daniel Ari Friedman
"""Separate summary predicates from practical declarations and reject duplicate slices."""

from pathlib import Path

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.review_timing import MEMBER, RESIDENT, build_timing_atlas, timing_summary
from blakean_federalism.review_timing_models import TimingConfiguration

ROOT = Path(__file__).parents[1]


def test_group_counts_follow_input_vectors_without_practical_status_scoring():
    # Given the supplied atlas, summarize its seven predicates without an extra status condition.
    atlas = build_timing_atlas(ROOT)
    result = timing_summary(atlas)
    observed = {(g.stratum_id, g.mode): g for g in result.groups}
    keys = {(c.configuration.stratum_id, c.configuration.mode) for c in atlas.cells}
    assert len(observed) == len(result.groups) == len(keys)
    assert set(observed) == keys
    assert any(g.all_formal_conditions > 0 for g in result.groups)
    for key in keys:
        cells = [
            c for c in atlas.cells if (c.configuration.stratum_id, c.configuration.mode) == key
        ]
        group = observed[key]
        assert group.configurations == len(cells)
        assert group.all_formal_conditions == sum(all(c.review.conditions) for c in cells)
        for identity, count in (
            (RESIDENT, group.resident_zero_gap),
            (MEMBER, group.member_zero_gap),
        ):
            expected = sum(
                not p.uncovered_intervals
                for c in cells
                for p in c.review.claimants
                if p.claimant_id == identity
            )
            assert count == expected


def test_duplicate_slice_membership_refuses_at_admission():
    # Given a duplicate membership, parsing refuses instead of double-counting its denominator.
    with pytest.raises(ResearchError, match="timing_duplicate_slice"):
        TimingConfiguration.model_validate(
            {
                "configuration_id": "control",
                "stratum_id": "early-threat",
                "response_hour": 20,
                "resident_ready_hour": 6,
                "mode": "none",
                "band": None,
                "slices": ["geometry", "geometry"],
            }
        )
