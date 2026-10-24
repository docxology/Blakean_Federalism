# Copyright (c) 2026 Daniel Ari Friedman
"Real files and PDFs exercise source, rights, layout and failure boundaries."

import io
import json

import pytest
from markdown_it import MarkdownIt
from PIL import Image
from pydantic import ValidationError
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.manuscript import ManuscriptSpec, VerseParser, validate_manuscript
from blakean_federalism.models import ResearchError
from blakean_federalism.storage import digest
from tools.acquire_manuscript import acquire
from tools.render_manuscript import body_pages, box, fonts, inline, render, text


@pytest.fixture
def manuscript(tmp_path):
    assets = []
    for name in ("M32", "J52", "J54", "J73"):
        path = tmp_path / (name + ".png")
        Image.new("RGB", (20, 30), "white").save(path)
        assets.append(
            dict(
                asset_id=name,
                path=path.name,
                url="https://example.org/image",
                sha256=digest(path),
                size=path.stat().st_size,
                kind="image",
                caption="Synthetic test image; not a Blake reproduction",
                rights_basis="Test fixture",
                credit="Test",
                rights_url="https://example.org",
            )
        )
    html = tmp_path / "source.html"
    html.write_text(
        '<br><a name="M1.1;E1"></a><font size="-2">locator</font>'
        "Persons &amp; states<sup>editorial note</sup><br>"
    )
    assets.append(
        dict(
            asset_id="text",
            path=html.name,
            url="https://example.org/text",
            sha256=digest(html),
            size=html.stat().st_size,
            kind="html",
        )
    )
    quotes = [
        dict(
            quote_id=q,
            asset_id="text",
            locator="Synthetic M1.1; E1",
            segments=[dict(anchor="M1.1;E1", occurrence=0, text="Persons & states")],
            context="Synthetic test only",
        )
        for q in ("Q03", "Q05", "Q07", "Q08")
    ]
    spec = ManuscriptSpec.model_validate(
        dict(
            version="0.2.0",
            assets=assets,
            quotations=quotes,
            fronts=["composition", "warrants", "authority", "countermodels"],
        )
    )
    for folder in ("research", "docs/manuscript", "src/blakean_federalism"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "research/manuscript-inputs.json").write_text(spec.model_dump_json())
    (tmp_path / "docs/manuscript/states-change.md").write_text(
        "# Synthetic article\n\n> Persons & states\n\n"
        "A **real** PDF with *italics* and [source](https://example.org).\n"
    )
    (tmp_path / "docs/manuscript/references-and-rights.md").write_text(
        "## Sources\n\nSynthetic rights.\n"
    )
    (tmp_path / "src/blakean_federalism/manuscript.py").write_text("# synthetic receipt binding\n")
    return tmp_path, spec


def test_real_source_and_pdf_roundtrip(manuscript):
    root, spec = manuscript
    assert validate_manuscript(root, spec, "> Persons & states\n")
    target = render(root, root / "analysis_output/positive")
    reader = PdfReader(target)
    assert len(reader.pages) == 9
    for number, phrase in enumerate(
        (
            "States Change",
            "From text to political argument",
            "Who may classify",
            "Scale does not establish freedom",
        )
    ):
        assert phrase in reader.pages[number].extract_text()
        assert str(number + 1) in reader.pages[number].extract_text()
    assert "Synthetic article" in reader.pages[4].extract_text()
    assert "A real PDF with italics and source." in reader.pages[4].extract_text()
    for page in reader.pages:
        assert list(page.mediabox) == [0, 0, 612, 792]
    receipt = json.loads((target.parent / "render-receipt.json").read_text())
    assert receipt["pdf_sha256"] == digest(target)
    assert receipt["body_start_page"] == 5
    assert (target.parent / "FONT-LICENSE.txt").stat().st_size > 1000
    original = target.read_bytes()
    with pytest.raises(FileExistsError):
        render(root, target.parent)
    assert target.read_bytes() == original


@pytest.mark.parametrize(
    "mutation",
    [
        "fronts",
        "duplicate_asset",
        "rights",
        "duplicate_quote",
        "unknown_source",
        "missing_anchor",
        "occurrence",
        "changed_text",
        "missing_quote",
        "unverified_quote",
        "corrupt_input",
        "symlink",
    ],
)
def test_real_negative_controls(manuscript, mutation):
    root, spec = manuscript
    data = spec.model_dump(mode="json")
    markdown = "> Persons & states\n"
    if mutation == "fronts":
        data["fronts"].reverse()
    elif mutation == "duplicate_asset":
        data["assets"].append(data["assets"][0])
    elif mutation == "rights":
        data["assets"][0]["rights_basis"] = ""
    elif mutation == "duplicate_quote":
        data["quotations"].append(data["quotations"][0])
    elif mutation == "unknown_source":
        data["quotations"][0]["asset_id"] = "missing"
    elif mutation == "missing_anchor":
        data["quotations"][0]["segments"][0]["anchor"] = "absent"
    elif mutation == "occurrence":
        data["quotations"][0]["segments"][0]["occurrence"] = 1
    elif mutation == "changed_text":
        data["quotations"][0]["segments"][0]["text"] = "A false quotation"
    elif mutation == "missing_quote":
        markdown = "No blockquote"
    elif mutation == "unverified_quote":
        markdown += "\n> Invented quotation\n"
    elif mutation == "corrupt_input":
        (root / "source.html").write_text("corrupted")
    elif mutation == "symlink":
        original = root / "source.html"
        original.rename(root / "actual.html")
        original.symlink_to(root / "actual.html")
    with pytest.raises(ResearchError):
        validate_manuscript(root, ManuscriptSpec.model_validate(data), markdown)


def test_schema_rejects_unknown_fields_and_negative_occurrence(manuscript):
    _, spec = manuscript
    with pytest.raises(ValidationError):
        ManuscriptSpec.model_validate(spec.model_dump() | {"secret_clearance": True})
    data = spec.model_dump(mode="json")
    data["quotations"][0]["segments"][0]["occurrence"] = -1
    with pytest.raises(ValidationError):
        ManuscriptSpec.model_validate(data)


def test_parser_keeps_repeated_anchors_and_excludes_editorial_type():
    parser = VerseParser()
    parser.feed(
        '<p><br><a name="J52;E200"></a><font size="-2">label'
        "<font>nested</font></font>A &amp; B<sup>not verse</sup></p>"
        '<br><a name="J52;E200"></a>Second <a name="bookmark"></a>line'
    )
    parser.finish()
    assert parser.lines == {"J52;E200": ["A & B", "Second line"]}


@pytest.mark.parametrize("relative", ["../outside", "other/folder", "analysis_output/../escape"])
def test_renderer_output_boundary(manuscript, relative):
    root, _ = manuscript
    with pytest.raises(ResearchError, match="output_boundary"):
        render(root, root / relative)


def test_renderer_rejects_symlink_output(manuscript):
    root, _ = manuscript
    (root / "analysis_output").symlink_to(root / "docs", target_is_directory=True)
    with pytest.raises(ResearchError, match="symlink_output"):
        render(root, root / "analysis_output/escape")


def test_unsupported_markdown_and_links_fail_explicitly():
    fonts()
    with pytest.raises(ResearchError, match="unsupported_markdown"):
        body_pages("- unhandled list\n")
    token = MarkdownIt().parse("[bad](http://example.org)")[1]
    with pytest.raises(ResearchError, match="link_scheme"):
        inline(token)
    token = MarkdownIt().parse("![missing](https://example.org/image)")[1]
    with pytest.raises(ResearchError, match="unsupported_inline"):
        inline(token)
    result = body_pages(
        "# Heading\n\n## Two\n\n### Three\n\n#### Four\n\n"
        "**bold** and *italic* and \x60code\x60.  \nHard break.\n"
    )
    assert "Hard break." in PdfReader(io.BytesIO(result)).pages[0].extract_text()


def test_real_geometry_rejects_overflow():
    fonts()
    canvas = Canvas(io.BytesIO())
    with pytest.raises(ResearchError, match="front_overflow"):
        text(canvas, "too low", 40, 40, 200, 10)
    with pytest.raises(ResearchError, match="diagram_overflow"):
        box(canvas, 40, 600, 200, 20, "Long box", "A description")


@pytest.mark.parametrize("mutation", ["none", "url", "path", "corrupt"])
def test_acquisition_preserves_verified_inputs_and_rejects_unsafe_records(manuscript, mutation):
    root, spec = manuscript
    data = spec.model_dump(mode="json")
    for asset in data["assets"]:
        original = root / asset["path"]
        target = root / "local_data/manuscript/v0.2.0" / original.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.read_bytes())
        asset["path"] = target.relative_to(root).as_posix()
        asset["url"] = "https://blake.lib.asu.edu/html/milton.html"
    if mutation == "url":
        data["assets"][0]["url"] = "https://example.org/unapproved"
    elif mutation == "path":
        data["assets"][0]["path"] = "local_data/manuscript/v0.2.0/../escape"
    elif mutation == "corrupt":
        (root / data["assets"][0]["path"]).write_bytes(b"corrupt")
    (root / "research/manuscript-inputs.json").write_text(json.dumps(data))
    if mutation == "none":
        assert acquire(root) == 0
    else:
        with pytest.raises(ResearchError):
            acquire(root)
