# Copyright (c) 2026 Daniel Ari Friedman
"""A fixed, inspectable catalog that preserves the conditions generating obligations."""

import json
from typing import TYPE_CHECKING, cast

from .institutional_experiment_models import FieldChange, Intervention, InterventionSpec
from .institutions import assess
from .models import Decision, ResearchError

if TYPE_CHECKING:
    from collections.abc import Sequence


def _change(path: str, *, value: str | bool | tuple[str, ...], blank: bool = False) -> FieldChange:
    return FieldChange(path=tuple(path.split(".")), value=value, only_if_blank=blank)


CATALOG = (
    InterventionSpec(
        intervention=Intervention.NONCAPTURE,
        label="Limit the role's identity claim",
        rule="CAPTURE",
        changes=(_change("claims_exhaust_person", value=False),),
    ),
    InterventionSpec(
        intervention=Intervention.UNRANKED_RIGHTS,
        label="Remove vision-based civic rank",
        rule="VISION_HIERARCHY",
        changes=(_change("vision_rank_determines_rights", value=False),),
    ),
    InterventionSpec(
        intervention=Intervention.EQUAL_PERSONHOOD,
        label="Establish equal personhood",
        rule="RIGHTS_FLOOR",
        changes=(_change("equal_personhood", value=True),),
    ),
    InterventionSpec(
        intervention=Intervention.OPEN_AFFILIATION,
        label="Allow overlapping affiliations",
        rule="FORCED_REGISTER",
        changes=(_change("forced_exclusive_national_register", value=False),),
    ),
    InterventionSpec(
        intervention=Intervention.PUBLIC_REASONS,
        label="Supply public reasons and voice limits",
        rule="TRANSLATION_OBLIGATION",
        changes=(
            _change(
                "asserting_authority.public_reason",
                value="Synthetic intervention: accessible reasons for the specified decision",
                blank=True,
            ),
            _change(
                "asserting_authority.representation_limits",
                value="Synthetic intervention: no claim to exhaust members' or nonmembers' voices",
                blank=True,
            ),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.CHARTER,
        label="Stipulate a separate competence source",
        rule="POETRY_TO_POWER",
        changes=(
            _change("asserting_authority.competence_warrant", value="stipulated_charter"),
            _change(
                "asserting_authority.competence_source",
                value="Counterfactual charter: separately stipulates the recorded competence",
            ),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.COMPETENCE,
        label="Specify competence, reach and enforcement",
        rule="AUTHORITY_GAP",
        changes=(
            _change(
                "asserting_authority.assigned_competence",
                value="Synthetic intervention: limited competence for the recorded action",
                blank=True,
            ),
            _change(
                "asserting_authority.competence_source",
                value="Synthetic intervention: explicit competence instrument",
                blank=True,
            ),
            _change(
                "asserting_authority.enforcement_actor",
                value="Synthetic intervention: named reviewable enforcement actor",
                blank=True,
            ),
            _change(
                "asserting_authority.enforcement_limits",
                value="Synthetic intervention: specified limits and independent review",
                blank=True,
            ),
            _change(
                "asserting_authority.reach",
                value=(
                    "Synthetic intervention: the recorded affected population and decision area",
                ),
                blank=True,
            ),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.CONTESTATION,
        label="Supply forum, voice and revision",
        rule="CONTESTATION",
        changes=(
            _change(
                "contestation.forum",
                value="Synthetic intervention: accessible independent review forum",
                blank=True,
            ),
            _change(
                "contestation.voice",
                value="Synthetic intervention: funded participation and dissent",
                blank=True,
            ),
            _change(
                "contestation.revision",
                value="Synthetic intervention: affected persons may initiate revision",
                blank=True,
            ),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.SUPPORTED_EXIT,
        label="Support practical passage and exit",
        rule="FORMAL_EXIT_ONLY",
        changes=(
            _change(
                "contestation.exit",
                value="Synthetic intervention: portable rights and supported affiliation change",
                blank=True,
            ),
            _change("contestation.materially_supported_exit", value=True),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.NONMEMBER_STANDING,
        label="Give affected nonmembers standing",
        rule="EXCLUDED_AFFECTED",
        changes=(_change("consequence.nonmember_standing", value=True),),
    ),
    InterventionSpec(
        intervention=Intervention.BURDEN_ALLOCATION,
        label="Specify costs, residual risk and remedies",
        rule="RESOURCE_GAP",
        changes=(
            _change(
                "consequence.burden_allocation",
                value="Synthetic allocation: payers, access floor, residual risks, remedies",
                blank=True,
            ),
        ),
    ),
    InterventionSpec(
        intervention=Intervention.TREATY_AND_REFUSAL,
        label="Address treaty and refusal separately",
        rule="FORCED_INCORPORATION",
        changes=(_change("treaty_or_refusal_addressed", value=True),),
    ),
)


def _is_declared(value: object) -> bool:
    return isinstance(value, Intervention)


def selected_catalog(available: tuple[Intervention, ...]) -> tuple[InterventionSpec, ...]:
    values: tuple[object, ...] = available
    if any(not _is_declared(value) for value in values) or len(set(available)) != len(available):
        raise ResearchError(
            "intervention_catalog", "Require distinct declared intervention identifiers"
        )
    return tuple(spec for spec in CATALOG if spec.intervention in available)


def rule_is_triggered(record: Decision, code: str) -> bool:
    conditional = {
        "POETRY_TO_POWER": record.consequence.coercive,
        "AUTHORITY_GAP": record.consequence.coercive,
        "EXCLUDED_AFFECTED": bool(record.consequence.affected_nonmembers),
        "RESOURCE_GAP": record.consequence.resource_decision,
        "FORCED_INCORPORATION": record.treaty_or_refusal_implicated,
    }
    if code not in {check.code for check in assess(record).checks}:
        raise ResearchError("unknown_rule", code)
    return conditional.get(code, True)


def _has_content(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (tuple, list)):
        items = cast("Sequence[object]", value)
        return bool(items) and all(isinstance(item, str) and item.strip() for item in items)
    return bool(value)


def _set_change(payload: dict[str, object], change: FieldChange) -> None:
    container = payload
    for key in change.path[:-1]:
        container = cast("dict[str, object]", container[key])
    key = change.path[-1]
    if not change.only_if_blank or not _has_content(container[key]):
        container[key] = change.value


def apply_interventions(record: Decision, interventions: tuple[Intervention, ...]) -> Decision:
    """Edit only a selected operator's failed predicate; inactive/satisfied operators are no-ops."""
    payload: dict[str, object] = record.model_dump(mode="python")
    failures = {finding.code for finding in assess(record).findings}
    for spec in selected_catalog(interventions):
        if spec.rule in failures:
            for change in spec.changes:
                _set_change(payload, change)
    changed = Decision.model_validate(payload)
    verify_protected_context(record, changed)
    return changed


def protected_context(record: Decision) -> str:
    """Canonical bytes for all fields outside the declared intervention domain."""
    payload: dict[str, object] = record.model_dump(mode="json")
    for spec in CATALOG:
        for change in spec.changes:
            container = payload
            for key in change.path[:-1]:
                container = cast("dict[str, object]", container[key])
            _ = container.pop(change.path[-1], None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def verify_protected_context(before: Decision, after: Decision) -> None:
    """Reject any intervention that changes fields outside the declared domain."""
    if protected_context(before) != protected_context(after):
        raise ResearchError("intervention_context", "An intervention changed protected context")
