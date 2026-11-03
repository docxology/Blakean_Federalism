# Copyright (c) 2026 Daniel Ari Friedman
"Real files and PDFs exercise source, rights, layout and failure boundaries."

import io
import json
import shutil

import pytest
from markdown_it import MarkdownIt
from pydantic import ValidationError
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from blakean_federalism.manuscript import ManuscriptSpec, VerseParser, validate_manuscript
from blakean_federalism.models import ResearchError
from blakean_federalism.storage import digest
from tools.acquire_manuscript import acquire
from tools.render_manuscript import body_pages, box, fonts, inline, render, text


def test_real_source_and_pdf_roundtrip(manuscript):
    root, spec = manuscript
    assert validate_manuscript(root, spec, "> Persons & states\n\n" * 4)
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
    markdown = "> Persons & states\n\n" * 4
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


@pytest.mark.parametrize("epoch", ["v0.2.0", "v0.11.0"])
@pytest.mark.parametrize("mutation", ["none", "url", "path", "corrupt"])
def test_acquisition_preserves_verified_inputs_and_rejects_unsafe_records(
    manuscript, mutation, epoch
):
    root, spec = manuscript
    data = spec.model_dump(mode="json")
    for asset in data["assets"]:
        original = root / asset["path"]
        target = root / "local_data/manuscript" / epoch / original.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.read_bytes())
        asset["path"] = target.relative_to(root).as_posix()
        asset["url"] = "https://blake.lib.asu.edu/html/milton.html"
    if mutation == "url":
        data["assets"][0]["url"] = "https://example.org/unapproved"
    elif mutation == "path":
        data["assets"][0]["path"] = f"local_data/manuscript/{epoch}/../escape"
    elif mutation == "corrupt":
        (root / data["assets"][0]["path"]).write_bytes(b"corrupt")
    (root / "research/manuscript-inputs.json").write_text(json.dumps(data))
    if mutation == "none":
        assert acquire(root) == 0
    else:
        expected = {
            "url": "source_url",
            "path": "acquisition_boundary",
            "corrupt": "checksum_mismatch",
        }[mutation]
        with pytest.raises(ResearchError, match=expected):
            acquire(root)


@pytest.mark.parametrize("field", ["caption", "rights_basis", "credit", "rights_url"])
def test_whitespace_cannot_supply_image_rights(manuscript, field):
    root, spec = manuscript
    assets = (spec.assets[0].model_copy(update={field: " \t "}), *spec.assets[1:])
    with pytest.raises(ResearchError, match="image_rights"):
        validate_manuscript(
            root, spec.model_copy(update={"assets": assets}), "> Persons & states\n\n" * 4
        )


def test_duplicate_and_missing_quotation_multiplicities_fail(manuscript):
    root, spec = manuscript
    for copies in (3, 5):
        with pytest.raises(ResearchError, match="manuscript_quotation"):
            validate_manuscript(root, spec, "> Persons & states\n\n" * copies)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org",
        "https://name:secret@example.org",
        "https://example.org/a b",
        "https://example.org/\\a",
    ],
)
def test_unsafe_source_urls_fail_before_rendering(manuscript, url):
    root, spec = manuscript
    assets = (spec.assets[0].model_copy(update={"url": url}), *spec.assets[1:])
    with pytest.raises(ResearchError, match="source_url"):
        validate_manuscript(
            root, spec.model_copy(update={"assets": assets}), "> Persons & states\n\n" * 4
        )


def test_layout_requires_the_selected_four_plate_images(manuscript):
    root, spec = manuscript
    with pytest.raises(ResearchError, match="image_set"):
        validate_manuscript(
            root, spec.model_copy(update={"assets": spec.assets[1:]}), "> Persons & states\n\n" * 4
        )


def test_pdf_is_byte_identical_across_independent_input_locations(manuscript):
    root, _ = manuscript
    second = root.parent / (root.name + "-different-location")
    shutil.copytree(root, second)
    first_pdf = render(root, root / "analysis_output/first")
    second_pdf = render(second, second / "analysis_output/second")
    assert first_pdf.read_bytes() == second_pdf.read_bytes()


@pytest.mark.parametrize("missing", [None, "J27", "J99", "unexpected"])
def test_new_selection_requires_exact_six_plates_while_old_epoch_stays_valid(manuscript, missing):
    root, spec = manuscript
    markdown = "> Persons & states\n\n" * 4
    assert validate_manuscript(root, spec, markdown)
    data = spec.model_dump(mode="json")
    data["version"] = "0.5.0"
    template = next(a for a in data["assets"] if a["kind"] == "image")
    data["assets"].extend([template | {"asset_id": name} for name in ("J27", "J99")])
    if missing in ("J27", "J99"):
        data["assets"] = [a for a in data["assets"] if a["asset_id"] != missing]
    if missing == "unexpected":
        data["assets"].append(template | {"asset_id": "J100"})
    current = ManuscriptSpec.model_validate(data)
    if missing is None:
        assert len(validate_manuscript(root, current, markdown)) == len(current.assets)
    else:
        with pytest.raises(ResearchError, match="image_set"):
            validate_manuscript(root, current, markdown)


@pytest.mark.parametrize(
    "version",
    [
        "0.6.0",
        "0.7.0",
        "0.8.0",
        "0.9.0",
        "0.10.0",
        "0.11.0",
        "0.12.0",
        "0.13.0",
        "0.14.0",
        "0.15.0",
    ],
)
@pytest.mark.parametrize("missing", [None, "J55", "J91", "J99", "unexpected"])
def test_plate_epoch_requires_every_identified_impression(manuscript, missing, version):
    root, spec = manuscript
    data = spec.model_dump(mode="json")
    data["version"] = version
    template = next(a for a in data["assets"] if a["kind"] == "image")
    data["assets"].extend(
        [template | {"asset_id": name} for name in ("J27", "J99", "J55", "J91", "J12", "J61")]
    )
    if version in ("0.8.0", "0.9.0", "0.10.0", "0.11.0", "0.12.0", "0.13.0", "0.14.0", "0.15.0"):
        data["assets"].append(template | {"asset_id": "J59"})
    if version in ("0.9.0", "0.10.0", "0.11.0", "0.12.0", "0.13.0", "0.14.0", "0.15.0"):
        data["assets"].append(template | {"asset_id": "J98"})
    if version in ("0.11.0", "0.12.0", "0.13.0", "0.14.0", "0.15.0"):
        data["assets"].extend(template | {"asset_id": name} for name in ("J1", "J100"))
    if missing == "unexpected":
        data["assets"].append(template | {"asset_id": "J101"})
    elif missing:
        data["assets"] = [a for a in data["assets"] if a["asset_id"] != missing]
    current = ManuscriptSpec.model_validate(data)
    if missing is None:
        assert len(validate_manuscript(root, current, "> Persons & states\n\n" * 4)) == len(
            current.assets
        )
    else:
        with pytest.raises(ResearchError, match="image_set"):
            validate_manuscript(root, current, "> Persons & states\n\n" * 4)
