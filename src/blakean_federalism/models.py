# Copyright (c) 2026 Daniel Ari Friedman
"""Parse source and institutional records once, preserving distinct warrant types."""

from enum import StrEnum
from typing import Literal, NewType

from blake.methods.models import (
    Concordance as SharedConcordance,
)
from blake.methods.models import (
    CountRow,
    Digest,
    FileReceipt,
    FrozenModel,
    Hit,
    ImportReceipt,
    Plane,
    Projection,
    QuerySpec,
    ResearchError,
    Role,
)
from blake.methods.models import ProjectionCorpusPin as CorpusPin
from blake.methods.models import ProjectionPassage as Passage

EntityId = NewType("EntityId", str)


class Concordance(SharedConcordance):
    """The shared evidence schema with this paper's interpretation ceiling."""

    interpretation: str = (
        "Whole-word explicit variants; source-document counts retain copy repetition. "
        "XML includes markup/apparatus. Mixed Erdman pages are not promoted to primary authorship. "
        "Occurrences are retrieval leads, not readings, unique works, or political entailments."
    )


class EntityKind(StrEnum):
    PERSON = "person"
    COLLECTIVE = "collective"
    NATION = "nation"
    POETIC_STATE = "poetic_state"
    JURISDICTION = "jurisdiction"
    INSTITUTION = "institution"


class EntityRef(FrozenModel):
    entity_id: EntityId
    kind: EntityKind
    label: str


class Warrant(StrEnum):
    TEXTUAL = "textual"
    INTERPRETIVE = "interpretive"
    NORMATIVE = "normative"
    STIPULATED_CHARTER = "stipulated_charter"
    EMPIRICAL = "empirical"


class Authority(FrozenModel):
    institution: EntityRef
    issuing_jurisdiction: EntityRef
    issuing_level: str
    assigned_competence: str
    competence_warrant: Warrant
    competence_source: str
    reach: tuple[str, ...]
    enforcement_actor: str
    enforcement_limits: str
    public_reason: str
    representation_limits: str


class Consequence(FrozenModel):
    action: str
    coercive: bool
    affected_persons: tuple[EntityId, ...]
    affected_nonmembers: tuple[EntityId, ...]
    nonmember_standing: bool
    resource_decision: bool
    burden_allocation: str


class Contestation(FrozenModel):
    forum: str
    voice: str
    exit: str
    materially_supported_exit: bool
    revision: str


class Decision(FrozenModel):
    """A proposed project schema, not a schema or legal holding in Entomological Law."""

    decision_id: str
    scenario_id: str
    alternative: str
    subject: EntityRef
    poetic_state_interpretation: str | None
    national_affiliations: tuple[EntityId, ...]
    assigned_legal_role: str
    temporal_scope: str
    classification_warrant: Warrant
    classification_source: str
    asserting_authority: Authority
    consequence: Consequence
    contestation: Contestation
    equal_personhood: bool
    claims_exhaust_person: bool
    vision_rank_determines_rights: bool
    forced_exclusive_national_register: bool
    treaty_or_refusal_implicated: bool
    treaty_or_refusal_addressed: bool
    provenance: Literal["synthetic institutional test; no actual legal determination"]


class Finding(FrozenModel):
    code: str
    detail: str


class RuleCheck(FrozenModel):
    code: str
    detail: str
    passed: bool


class Assessment(FrozenModel):
    schema_version: Literal[2] = 2
    checks: tuple[RuleCheck, ...]

    decision_id: str
    admissible_under_proposed_rules: bool
    findings: tuple[Finding, ...]
    meaning: str = (
        "Consistency with stipulated project norms, not legality, empirical freedom, "
        "political legitimacy, or a deduction from Blake."
    )


__all__ = [
    "Assessment",
    "Authority",
    "Concordance",
    "Consequence",
    "Contestation",
    "CorpusPin",
    "CountRow",
    "Decision",
    "Digest",
    "EntityKind",
    "EntityRef",
    "FileReceipt",
    "Finding",
    "FrozenModel",
    "Hit",
    "ImportReceipt",
    "Passage",
    "Plane",
    "Projection",
    "QuerySpec",
    "ResearchError",
    "Role",
    "RuleCheck",
    "Warrant",
]
