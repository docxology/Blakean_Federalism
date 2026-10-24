# Copyright (c) 2026 Daniel Ari Friedman
"""Parse source and institutional records once, preserving distinct warrant types."""

from enum import StrEnum
from typing import Annotated, ClassVar, Literal, NewType

from pydantic import BaseModel, ConfigDict, Field, model_validator

EntityId = NewType("EntityId", str)
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class FrozenModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")


class ResearchError(Exception):
    """An evidence boundary was violated."""

    def __init__(self, code: str, detail: str) -> None:
        self.code: str = code
        self.detail: str = detail
        super().__init__(f"{code}: {detail}")


class Plane(StrEnum):
    READING = "reading"
    ERDMAN = "erdman"
    XML = "xml"


class Role(StrEnum):
    PRIMARY = "primary"
    EDITORIAL = "editorial"
    UNVERIFIED = "unverified"


class Passage(FrozenModel):
    passage_id: str
    work_id: str
    author_id: str
    title: str
    edition_id: str
    edition: str
    copy_id: str | None = None
    locator: str
    locator_kind: Literal["plate", "page", "folio", "file_lines", "section"]
    source_url: str
    rights: str
    text_role: Role
    source_plane: Plane
    text: str
    source_sha256: Digest | None = None

    @model_validator(mode="after")
    def preserve_primary_plane(self) -> "Passage":
        if self.text_role == Role.PRIMARY and self.source_plane != Plane.READING:
            raise ResearchError("primary_plane", self.passage_id)
        return self


class FileReceipt(BaseModel):
    # The upstream receipt may add metadata; only these fields bind consumed bytes.
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    path: str
    size: int = Field(ge=0)
    sha256: Digest


class Projection(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    captured_manifest_sha256: Digest
    index: FileReceipt
    inputs: tuple[FileReceipt, ...]
    passages: int = Field(ge=1)
    passage_ids: tuple[str, ...]
    passages_by_plane: dict[Plane, int]
    passages_by_role: dict[Role, int]


class CorpusPin(FrozenModel):
    upstream_commit: str
    captured_manifest_sha256: Digest
    projection_manifest_sha256: Digest
    projection_relative_path: str
    index_sha256: Digest
    unresolved_images: int = Field(ge=0)
    scope_note: str


class ImportReceipt(FrozenModel):
    schema_version: Literal[1] = 1
    corpus_pin: CorpusPin
    passages: int
    consumed_inputs_verified: int
    passages_by_plane: dict[Plane, int]
    passages_by_role: dict[Role, int]
    source_capture_path: str
    independence: Literal["copied bytes; no upstream writes or linked payloads"]


class QuerySpec(FrozenModel):
    query_id: str
    variants: tuple[str, ...] = Field(min_length=1)
    note: str


class Hit(FrozenModel):
    query_id: str
    passage_id: str
    work_id: str
    title: str
    edition_id: str
    locator: str
    source_url: str
    plane: Plane
    role: Role
    text_sha256: Digest
    start: int
    end: int
    expression: str
    context: str


class CountRow(FrozenModel):
    query_id: str
    plane: Plane
    role: Role
    occurrences: int
    matched_source_documents: int


class Concordance(FrozenModel):
    schema_version: Literal[1] = 1
    pin: CorpusPin
    query_sha256: Digest
    scanned_source_documents: int
    rows: tuple[CountRow, ...]
    hits: tuple[Hit, ...]
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
