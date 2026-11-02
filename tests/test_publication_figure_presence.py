# Copyright (c) 2026 Daniel Ari Friedman
"""A figure identifier on text or a link cannot stand in for a rendered image."""

import pytest

from blakean_federalism.models import ResearchError
from blakean_federalism.publication_models import ReferenceContract
from blakean_federalism.publication_verification import NumberedBlocks, verify_references


def contract():
    return ReferenceContract(
        formalism_numbers={},
        formalism_titles={},
        bibliography_keys=(),
        cited_bibliography_keys=(),
        equation_labels=(),
        figure_labels=("fig:protected",),
        cross_references=(),
    )


@pytest.mark.parametrize(
    "html",
    [
        '<a id="fig:protected" href="figure.png">a caption</a>',
        '<span id="fig:protected">a caption</span>',
        '<figure id="fig:protected"><figcaption>empty</figcaption></figure>',
        '<figure id="fig:protected"><img></figure>',
        '<figure id="fig:protected"><img src="one.png"><img src="two.png"></figure>',
    ],
)
def test_nonimage_or_ambiguous_figure_refuses(html):
    document = NumberedBlocks()
    document.feed(html)
    with pytest.raises(ResearchError, match="rendered_figure_image"):
        verify_references(contract(), document, html, "")


def test_one_actual_image_with_its_figure_identifier_passes():
    html = '<figure id="fig:protected"><img src="figure.png"><figcaption>x</figcaption></figure>'
    document = NumberedBlocks()
    document.feed(html)
    verify_references(contract(), document, html, "")
