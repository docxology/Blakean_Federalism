# Copyright (c) 2026 Daniel Ari Friedman
"""Export complete raw person records with exact events, gaps and separate predicates."""

import csv
import io
import json

from .review_pressure_models import PressureIssue
from .review_timing import gap_topology
from .review_timing_models import TimingAtlas


def claimant_csv(atlas: TimingAtlas) -> str:
    """Retain raw events, each person's exact exposure and all separate condition fields."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        (
            "configuration_id",
            "stratum_id",
            "slices",
            "mode",
            "claimant_id",
            "membership",
            "available_hours",
            "support_hours",
            "required_hours",
            "ready_hour",
            "opens_hour",
            "closes_hour",
            "consequence_hour",
            "response_hour",
            "declared_band",
            "provider",
            "earliest_filing_hour",
            "filing_feasible",
            "active_protection",
            "uncovered_intervals",
            "uncovered_hours",
            "gap_topology",
            "standing",
            "may_remain",
            "sufficient_hours",
            "filing_ready",
            "timely_or_protected",
            "issuer_separated",
            "revision_power",
            "suspension_power",
            "all_formal_conditions",
            "unassessed_issues",
            *[issue.value for issue in PressureIssue],
        )
    )
    statuses = {b.issue: b.status.value for b in atlas.specification.practical_boundaries}
    for cell in atlas.cells:
        config, review = cell.configuration, cell.review
        audits = {p.claimant_id: p for p in review.claimants}
        for person in review.procedure.claimants:
            audit = audits[person.claimant_id]
            writer.writerow(
                (
                    config.configuration_id,
                    config.stratum_id,
                    "|".join(s.value for s in config.slices),
                    config.mode.value,
                    person.claimant_id,
                    person.membership.value,
                    person.available_filing_hours,
                    person.support_enabled_filing_hours,
                    person.required_filing_hours,
                    person.ready_to_file_hour,
                    review.procedure.filing_opens_hour,
                    review.procedure.filing_closes_hour,
                    person.consequence_hour,
                    review.procedure.response_hour,
                    json.dumps(
                        None
                        if config.band is None
                        else (config.band.starts_hour, config.band.ends_hour)
                    ),
                    "" if person.protection is None else person.protection.provider_office_id,
                    audit.earliest_filing_hour,
                    int(all(audit.conditions[:4])),
                    json.dumps(audit.active_protection),
                    json.dumps(audit.uncovered_intervals),
                    audit.uncovered_wait_hours,
                    gap_topology(cell, person.claimant_id).value,
                    *[int(c) for c in audit.conditions],
                    int(review.issuer_separated_forum),
                    int(review.revision_power),
                    int(review.suspension_power),
                    int(review.declared_conditions_hold),
                    "|".join(issue.value for issue in review.procedure.unassessed_issues),
                    *[statuses[issue] for issue in PressureIssue],
                )
            )
    return stream.getvalue()
