# Copyright (c) 2026 Daniel Ari Friedman
"""Private workspace policy and branding around the shared offline renderer."""

from importlib.resources import files
from pathlib import Path

from blake.methods.models import ProjectionCorpusPin as CorpusPin
from blake.methods.workspace import (
    RESOURCE_NAMES,
    SEMANTICS,
    WorkspaceBranding,
    unicode_search_tables,
)
from blake.methods.workspace import (
    build_search_workspace as _build,
)
from blake.methods.workspace import (
    csp_hash as _csp_hash,
)
from blake.methods.workspace import (
    json_script as _json_script,
)

from . import __version__


def build_search_workspace(directory: Path, pin: CorpusPin, output: Path) -> Path:
    """Publish private source texts only under the ignored analysis output root."""
    return _build(
        directory,
        pin,
        output,
        branding=WorkspaceBranding(
            title="Blake corpus · passage search",
            brand="BLAKEAN FEDERALISM / LOCAL RESEARCH INSTRUMENT",
            footer="Blakean Federalism  ·  Local corpus search.",
        ),
        producer_version=__version__,
        private_output_root=Path.cwd() / "analysis_output",
        resource_directory=Path(str(files("blakean_federalism").joinpath("resources"))),
    )


__all__ = [
    "RESOURCE_NAMES",
    "SEMANTICS",
    "_csp_hash",
    "_json_script",
    "build_search_workspace",
    "unicode_search_tables",
]
