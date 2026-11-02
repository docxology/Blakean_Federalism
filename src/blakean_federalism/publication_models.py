# Copyright (c) 2026 Daniel Ari Friedman
"""Typed source and native-execution contracts for the manuscript pipeline."""

from pydantic import Field, model_validator

from .models import Digest, FrozenModel, ResearchError


class ReferenceContract(FrozenModel):
    formalism_numbers: dict[str, str]
    formalism_titles: dict[str, str]
    bibliography_keys: tuple[str, ...]
    cited_bibliography_keys: tuple[str, ...]
    equation_labels: tuple[str, ...]
    figure_labels: tuple[str, ...]
    cross_references: tuple[str, ...]


class TemplateRendering(FrozenModel):
    schema_version: int
    source_date_epoch: int = Field(ge=0)
    repository: str
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    writers: tuple[str, ...]
    formalism_filter: str
    numbering: str
    bibliography: str
    runtime: str
    limits: tuple[str, ...]


class PreparedPublication(FrozenModel):
    producer_version: str
    inputs: dict[str, Digest]
    producers: dict[str, Digest] = Field(default_factory=dict)
    contract: ReferenceContract
    template: TemplateRendering
    source_order: tuple[str, ...]
    figures: dict[str, Digest]
    generated_schematics: dict[str, str]
    variables: dict[str, str]
    scope: str


class NativeReceipt(FrozenModel):
    template_repository: str
    template_commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    template_sources: dict[str, Digest]
    template_gitlinks: dict[str, str]
    template_sources_unchanged: bool
    runtime: dict[str, str]
    pdf: str
    html: str
    outputs: dict[str, Digest]
    resolved_inputs: dict[str, Digest]
    writer_calls: tuple[str, ...]
    scope: str

    @model_validator(mode="after")
    def exact_outputs(self) -> "NativeReceipt":
        if (
            self.pdf == self.html
            or set(self.outputs) != {self.pdf, self.html}
            or not self.template_sources_unchanged
        ):
            raise ResearchError(
                "native_receipt", "Exact current PDF and HTML bindings are required"
            )
        return self
