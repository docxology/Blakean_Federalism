# Copyright (c) 2026 Daniel Ari Friedman
"""Current producer versions retain their documented graphical analysis profile."""

import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError
from pypdf import PdfReader

from blakean_federalism.abstract_captions import uses_analytical_abstracts
from blakean_federalism.manuscript import ManuscriptSpec
from blakean_federalism.publication_figures import generate_figures
from blakean_federalism.publication_profiles import AUTHORITY_PRODUCERS, ILLUMINATED_EDITIONS

from .test_illuminated_abstracts import illuminated as illuminated_fixture
from .test_illuminated_abstracts import observed as observations_fixture
from .test_illuminated_abstracts import prepared as prepared_fixture

illuminated = illuminated_fixture
observed = observations_fixture
prepared = prepared_fixture


def test_current_producer_keeps_federated_authority_figure(illuminated, tmp_path):
    _, report, artwork = illuminated
    rasterizer = shutil.which("pdftoppm")
    assert rasterizer is not None
    output = tmp_path / "producer18"
    figures = generate_figures(
        report.model_copy(update={"producer_version": "0.18.0"}),
        output,
        rasterizer,
        artwork=artwork,
    )
    assert "federated-inference-authority" in figures
    page = PdfReader(output / "federated-inference-authority.pdf").pages[0]
    assert "must not erase a person's standing" in page.extract_text()
    assert (output / figures["federated-inference-authority"]).is_file()


@pytest.mark.parametrize(
    ("version", "authority", "analytical"),
    [
        ("0.11.0", False, False),
        ("0.12.0", True, False),
        ("0.13.0", True, False),
        ("0.14.0", True, True),
        ("0.15.0", True, True),
        ("0.16.0", True, True),
        ("0.17.0", True, True),
        ("0.18.0", True, True),
        ("0.19.0", True, True),
        ("0.20.0", False, False),
    ],
)
def test_explicit_profiles_preserve_archival_and_current_selection(
    illuminated, version, authority, analytical
):
    _, report, _ = illuminated
    assert (version in AUTHORITY_PRODUCERS) is authority
    # The older fixture has the art for drawing but no J1 catalog entry in its report.
    assert not uses_analytical_abstracts(report.model_copy(update={"producer_version": version}))
    source = Path(__file__).parents[1] / "research/manuscript-inputs.json"
    catalog = ManuscriptSpec.model_validate_json(source.read_bytes())
    frontispiece = next(asset for asset in catalog.assets if asset.asset_id == "J1")
    current = report.model_copy(
        update={"producer_version": version, "images": (*report.images, frontispiece)}
    )
    assert uses_analytical_abstracts(current) is analytical
    assert (version in ILLUMINATED_EDITIONS) is (version != "0.20.0")


@pytest.mark.parametrize("version", ["0.18.0", "0.19.0"])
def test_current_manuscript_spec_versions_are_admitted_without_mutating_historical_input(version):
    path = Path(__file__).parents[1] / "research/manuscript-inputs.json"
    original = path.read_bytes()
    data = json.loads(original)
    data["version"] = version
    assert ManuscriptSpec.model_validate_json(json.dumps(data)).version == version
    data["version"] = "0.20.0"
    with pytest.raises(ValidationError):
        ManuscriptSpec.model_validate_json(json.dumps(data))
    assert path.read_bytes() == original
