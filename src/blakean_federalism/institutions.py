# Copyright (c) 2026 Daniel Ari Friedman
"""Inspect explicit inferential transitions under proposed norms, without a freedom score."""

from .models import Assessment, Decision, EntityKind, Finding, RuleCheck, Warrant


def specified(*values: str) -> bool:
    """Whitespace cannot supply a missing warrant or remedy."""
    return all(value.strip() for value in values)


def assess(record: Decision) -> Assessment:
    """Apply inspectable predicates without ranking a population or ontology."""
    authority = record.asserting_authority
    outcome = record.consequence
    contest = record.contestation
    violations = (
        (
            authority.institution.kind != EntityKind.INSTITUTION,
            "ISSUER_TYPE",
            "An asserting authority requires an institution.",
        ),
        (
            authority.issuing_jurisdiction.kind != EntityKind.JURISDICTION,
            "JURISDICTION_TYPE",
            "Issuing jurisdiction differs from persons and reach.",
        ),
        (
            record.subject.kind in {EntityKind.POETIC_STATE, EntityKind.JURISDICTION},
            "SUBJECT_COLLAPSE",
            "Persons and collectives are not states or jurisdictions.",
        ),
        (record.claims_exhaust_person, "CAPTURE", "A role cannot exhaust a person's identity."),
        (record.vision_rank_determines_rights, "VISION_HIERARCHY", "Vision grants no civic rank."),
        (not record.equal_personhood, "RIGHTS_FLOOR", "Common standing must bind every body."),
        (
            record.forced_exclusive_national_register,
            "FORCED_REGISTER",
            "Political affiliation cannot be forced exclusive.",
        ),
        (
            not specified(authority.public_reason, authority.representation_limits),
            "TRANSLATION_OBLIGATION",
            "Explain accessible reasons and representation limits.",
        ),
        (
            outcome.coercive and authority.competence_warrant != Warrant.STIPULATED_CHARTER,
            "POETRY_TO_POWER",
            "Interpretation or evidence alone grants no coercive competence.",
        ),
        (
            outcome.coercive
            and (
                not specified(
                    authority.assigned_competence,
                    authority.competence_source,
                    authority.enforcement_actor,
                    authority.enforcement_limits,
                )
                or not authority.reach
                or not specified(*authority.reach)
            ),
            "AUTHORITY_GAP",
            "Competence, reach and enforcement must be specified.",
        ),
        (
            not specified(contest.forum, contest.voice, contest.revision),
            "CONTESTATION",
            "Appeal, voice and revision are required.",
        ),
        (
            not specified(contest.exit) or not contest.materially_supported_exit,
            "FORMAL_EXIT_ONLY",
            "Exit requires practical support.",
        ),
        (
            bool(outcome.affected_nonmembers) and not outcome.nonmember_standing,
            "EXCLUDED_AFFECTED",
            "Affected nonmembers require standing.",
        ),
        (
            outcome.resource_decision and not specified(outcome.burden_allocation),
            "RESOURCE_GAP",
            "Name payers, residual risks and remedies.",
        ),
        (
            record.treaty_or_refusal_implicated and not record.treaty_or_refusal_addressed,
            "FORCED_INCORPORATION",
            "Treaty and refusal require distinct treatment.",
        ),
    )
    findings = tuple(
        Finding(code=code, detail=detail) for failed, code, detail in violations if failed
    )
    return Assessment(
        decision_id=record.decision_id,
        checks=tuple(
            RuleCheck(code=code, detail=detail, passed=not failed)
            for failed, code, detail in violations
        ),
        admissible_under_proposed_rules=not findings,
        findings=findings,
    )
