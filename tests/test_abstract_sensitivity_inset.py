# Copyright (c) 2026 Daniel Ari Friedman
"""Real vector outputs must expose each defined omission estimate."""

from collections.abc import Mapping
from functools import partial
from pathlib import Path

from blakean_federalism.abstract_explanation import display_frequency
from blakean_federalism.abstract_layout import analytical_sources
from blakean_federalism.abstract_sensitivity_inset import source_sensitivity
from blakean_federalism.workbench_models import Workbench

from .test_analytical_abstracts import analytical as analytical_fixture
from .test_illuminated_abstracts import illuminated as illuminated_fixture
from .test_illuminated_abstracts import observed as observed_fixture
from .test_illuminated_abstracts import prepared as prepared_fixture
from .test_illuminated_abstracts import render

analytical = analytical_fixture
illuminated = illuminated_fixture
observed = observed_fixture
prepared = prepared_fixture


def test_each_defined_estimate_reaches_the_actual_vector_page(
    analytical: tuple[Path, Workbench, Mapping[str, Path]],
) -> None:
    # Given the real fixed corpus fixture and its two independently defined query rows.
    root, report, artwork = analytical
    source = analytical_sources(report, artwork)
    selected = [row for row in source.corpus if row.query_id in {"states", "imagination"}]
    # When the inset alone is rendered through the production vector writer.
    page = render(root / "omission-inset.pdf", partial(source_sensitivity, source=source))
    text = page.extract_text()
    # Then numerical labels and one circular point per defined pooled estimate survive.
    for row in selected:
        for rate in (row.loo_min_rate, row.loo_max_rate, row.pooled_rate):
            assert display_frequency(rate) in text
    curves = sum(operator == b"c" for _, operator in page.get_contents().operations)
    assert curves == 4 * sum(row.pooled_rate is not None for row in selected)
