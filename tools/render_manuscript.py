# Copyright (c) 2026 Daniel Ari Friedman
"""Render the private manuscript with four physical graphical-abstract pages.

Optional manuscript dependencies are isolated from the analytical CLI. Outputs
are exclusive new directories; no source or corpus data is rewritten.
"""

import io
import json
from functools import partial
from html import escape
from pathlib import Path

import reportlab
from markdown_it import MarkdownIt
from markdown_it.token import Token
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
)

from blakean_federalism import __version__
from blakean_federalism.manuscript import ManuscriptSpec, validate_manuscript
from blakean_federalism.models import ResearchError
from blakean_federalism.storage import digest, safe_path

PAGE = (612, 792)
MARGIN = 39.6
WIDTH = PAGE[0] - 2 * MARGIN
INK = colors.HexColor("#173737")
TEAL = colors.HexColor("#2a7069")
RUST = colors.HexColor("#995336")
PALE = colors.HexColor("#edf3f0")


def fonts() -> Path:
    directory = Path(reportlab.__file__).parent / "fonts"
    for name, filename in (
        ("Vera", "Vera.ttf"),
        ("Vera-Bold", "VeraBd.ttf"),
        ("Vera-Italic", "VeraIt.ttf"),
        ("Vera-BoldItalic", "VeraBI.ttf"),
    ):
        pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily(
        "Vera", normal="Vera", bold="Vera-Bold", italic="Vera-Italic", boldItalic="Vera-BoldItalic"
    )
    return directory


def style(name: str = "body", size: float = 10, **kwargs: object) -> ParagraphStyle:
    return ParagraphStyle(
        name,
        fontName=kwargs.pop("fontName", "Vera"),
        fontSize=size,
        leading=size * 1.28,
        textColor=kwargs.pop("textColor", INK),
        spaceAfter=7,
        **kwargs,
    )


def clean(text: str) -> str:
    return text.replace("\u2013", "-").replace("\u2014", " - ").replace("\u2011", "-")


def text(
    canvas: Canvas,
    content: str,
    x: float,
    top: float,
    width: float,
    size: float = 10,
    **kwargs: object,
) -> float:
    paragraph = Paragraph(content, style(size=size, **kwargs))
    _, height = paragraph.wrap(width, PAGE[1])
    if top - height < MARGIN:
        raise ResearchError("front_overflow", content[:80])
    paragraph.drawOn(canvas, x, top - height)
    return top - height


def box(
    canvas: Canvas,
    x: float,
    top: float,
    width: float,
    height: float,
    title: str,
    description: str,
    accent: colors.Color = TEAL,
) -> None:
    canvas.setFillColor(PALE)
    canvas.setStrokeColor(colors.HexColor("#cbd6d2"))
    canvas.setLineWidth(0.5)
    canvas.roundRect(x, top - height, width, height, 7, fill=1, stroke=1)
    bottom = text(
        canvas,
        escape(title),
        x + 11,
        top - 10,
        width - 22,
        11,
        fontName="Vera-Bold",
        textColor=accent,
    )
    bottom = text(canvas, escape(description), x + 11, bottom - 7, width - 22, 9)
    if bottom < top - height + 8:
        raise ResearchError("diagram_overflow", title)


def arrow(
    canvas: Canvas, x1: float, y1: float, x2: float, y2: float, color: colors.Color = TEAL
) -> None:
    canvas.setStrokeColor(color)
    canvas.setFillColor(color)
    canvas.setLineWidth(1.2)
    canvas.line(x1, y1, x2, y2)
    # All schematic links here run downward or rightward.
    path = canvas.beginPath()
    path.moveTo(x2, y2)
    if abs(x2 - x1) > abs(y2 - y1):
        path.lineTo(x2 - 5, y2 + 3)
        path.lineTo(x2 - 5, y2 - 3)
    else:
        path.lineTo(x2 - 3, y2 + 5)
        path.lineTo(x2 + 3, y2 + 5)
    path.close()
    canvas.drawPath(path, fill=1, stroke=0)


def footer(canvas: Canvas, number: int) -> None:
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN, 30, PAGE[0] - MARGIN, 30)
    canvas.setFont("Vera", 8)
    canvas.setFillColor(INK)
    canvas.drawString(MARGIN, 18, f"Blakean Federalism | {__version__} | Private research draft")
    canvas.drawRightString(PAGE[0] - MARGIN, 18, str(number))


def diagram(canvas: Canvas, number: int) -> None:
    left = MARGIN
    if number == 1:
        box(
            canvas,
            left,
            548,
            WIDTH,
            63,
            "STATES: enduring imaginative possibilities",
            (
                "S1 and S2 are schematic possibilities, not sovereign offices or an "
                "exhaustive ontology."
            ),
        )
        for offset in (85, 255, 425):
            arrow(canvas, left + offset, 479, left + offset, 441)
        for index, label in enumerate(("NATION A", "NATION B", "NATION C")):
            box(
                canvas,
                left + index * 182,
                435,
                169,
                76,
                label,
                "Temporal histories; several possibilities; no exclusive ownership.",
            )
        text(
            canvas,
            "Many-to-many interpretation; arrows do not confer authority.",
            left,
            347,
            WIDTH,
            9,
        )
        box(
            canvas,
            left,
            319,
            WIDTH,
            58,
            "PERSONS exceed every classification",
            "Affiliation can change. Basic standing and voice must survive passage.",
            RUST,
        )
    elif number == 2:
        entries = (
            (
                "TEXTUAL WARRANT",
                "What do the passage, speaker, edition and illuminated page support?",
            ),
            (
                "INTERPRETIVE BRIDGE",
                ("Which contemporary construction is proposed, and which countertext resists it?"),
            ),
            (
                "INSTITUTIONAL WARRANT",
                ("Who may decide, under what authority, with what remedies and material effects?"),
            ),
        )
        for index, (title, description) in enumerate(entries):
            top = 548 - index * 101
            box(canvas, left, top, WIDTH, 73, title, description)
            if index < 2:
                arrow(canvas, 306, top - 77, 306, top - 96)
        text(
            canvas,
            (
                "A verified quotation does not prove the bridge. A bridge does not authorize "
                "coercion."
            ),
            left,
            256,
            WIDTH,
            10,
            fontName="Vera-Bold",
        )
    elif number == 3:
        entries = (
            (
                "ENTITY + ASSIGNED ROLE",
                "Keep the person or collective distinct from its classification.",
            ),
            (
                "ASSERTING AUTHORITY + WARRANT",
                "Name the issuer, competence source and temporal limits.",
            ),
            (
                "CONSEQUENCE + CONTESTATION",
                "Specify reach, enforcement, costs, voice, exit and revision.",
            ),
        )
        for index, (title, description) in enumerate(entries):
            top = 548 - index * 101
            box(canvas, left, top, WIDTH, 73, title, description)
            if index < 2:
                arrow(canvas, 306, top - 77, 306, top - 96)
        text(
            canvas,
            (
                "Issuer / competence / reach / enforcement remain separate. This record is a "
                "new project extension."
            ),
            left,
            256,
            WIDTH,
            10,
            fontName="Vera-Bold",
        )
    else:
        box(
            canvas,
            left,
            548,
            WIDTH,
            62,
            "BROADER CULTURAL IDENTIFICATION",
            (
                "A speculative counter-model from Rahman's contributor profile, not a "
                "validated causal result."
            ),
        )
        arrow(canvas, 165, 479, 165, 444)
        arrow(canvas, 447, 479, 447, 444, RUST)
        box(
            canvas,
            left,
            435,
            254,
            80,
            "Coordination may improve",
            "Translation can make more reasons and relationships intelligible.",
        )
        box(
            canvas,
            left + 279,
            435,
            254,
            80,
            "Conformity may increase",
            "Gatekeepers can raise the cost of dissent or define it as noise.",
            RUST,
        )
        box(
            canvas,
            left,
            323,
            WIDTH,
            61,
            "MATERIAL TEST: water, work, land and unequal power",
            "Keep affected nonmembers, treaty relations, refusal and revision visible.",
        )


def opening_pages(spec: ManuscriptSpec, paths: dict[str, Path]) -> bytes:
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=PAGE, invariant=1)
    titles = (
        "States Change",
        "From text to political argument",
        "Who may classify - and act?",
        "Scale does not establish freedom",
    )
    subtitles = (
        "Blakean Federalism and composition without capture",
        "Graphical abstract 2 | Separate three kinds of warrant",
        "Graphical abstract 3 | Make authority inspectable",
        "Graphical abstract 4 | Preserve the counter-model",
    )
    ids = ("M32", "J52", "J54", "J73")
    quote_ids = ("Q03", "Q05", "Q07", "Q08")
    for number, (title, subtitle, image_id, quote_id) in enumerate(
        zip(titles, subtitles, ids, quote_ids, strict=True), start=1
    ):
        canvas.setFillColor(TEAL)
        text(
            canvas,
            "PRIVATE RESEARCH / DANIEL ARI FRIEDMAN / 23 OCTOBER 2026",
            MARGIN,
            751,
            WIDTH,
            8.5,
        )
        y = text(canvas, title, MARGIN, 721, WIDTH, 29 if number == 1 else 23, fontName="Vera-Bold")
        text(canvas, subtitle, MARGIN, y - 14, WIDTH, 13)
        text(
            canvas,
            "Graphical abstract 1 | The federation need not become one nation."
            if number == 1
            else (
                "Project-authored schematic. Political implications require independent argument."
            ),
            MARGIN,
            599,
            WIDTH,
            9,
        )
        diagram(canvas, number)
        image_asset = next(a for a in spec.assets if a.asset_id == image_id)
        canvas.drawImage(
            ImageReader(io.BytesIO(paths[image_id].read_bytes())),
            MARGIN,
            59,
            width=116,
            height=170,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        quote = next(q for q in spec.quotations if q.quote_id == quote_id)
        # A bounded excerpt of the ledger, with its complete locator retained.
        selected = quote.segments[:2] if number in (1, 3) else quote.segments
        text(
            canvas,
            "<br/>".join(escape(s.text) for s in selected),
            175,
            224,
            397,
            10,
            fontName="Vera-Italic",
        )
        shown_locator = {1: "Milton 32:22-23, E132", 3: "Jerusalem 54:1-2, E203"}.get(
            number, quote.locator
        )
        text(canvas, escape(clean(shown_locator)), 175, 155, 397, 8.5)
        text(canvas, escape(clean(image_asset.caption)), 175, 133, 397, 8)
        text(
            canvas,
            (
                "LOC item-specific no-known-restrictions advisory; not CC0. Full credits and "
                "plates follow."
            ),
            175,
            78,
            397,
            8,
        )
        footer(canvas, number)
        canvas.showPage()
    canvas.save()
    return stream.getvalue()


def inline(token: Token, *, verse: bool = False) -> str:
    result = []
    for child in token.children or []:
        kind = child.type
        if kind in ("text", "code_inline"):
            result.append(escape(clean(child.content)))
        elif kind in ("softbreak", "hardbreak"):
            result.append("<br/>" if kind == "hardbreak" or verse else " ")
        elif kind in ("strong_open", "strong_close", "em_open", "em_close"):
            result.append(
                {
                    "strong_open": "<b>",
                    "strong_close": "</b>",
                    "em_open": "<i>",
                    "em_close": "</i>",
                }[kind]
            )
        elif kind == "link_open":
            href = child.attrGet("href") or ""
            if not href.startswith("https://"):
                raise ResearchError("link_scheme", href)
            result.append('<a href="' + escape(href, quote=True) + '" color="#2a7069">')
        elif kind == "link_close":
            result.append("</a>")
        else:
            raise ResearchError("unsupported_inline", kind)
    return "".join(result)


def body_pages(markdown: str) -> bytes:
    tokens = MarkdownIt("commonmark").parse(markdown)
    styles = {
        "h1": style("h1", 21, fontName="Vera-Bold", keepWithNext=True, spaceBefore=12),
        "h2": style("h2", 14, fontName="Vera-Bold", keepWithNext=True, spaceBefore=9),
        "h3": style("h3", 12, fontName="Vera-Bold", keepWithNext=True, spaceBefore=10),
        "h4": style("h4", 10.5, fontName="Vera-Bold", keepWithNext=True, spaceBefore=8),
        "body": style(),
        "quote": style("quote", 9.4, leftIndent=12, rightIndent=8, borderPadding=7, backColor=PALE),
    }
    story = []
    heading = None
    quotation = False
    for token in tokens:
        kind = token.type
        if kind == "heading_open":
            heading = token.tag
        elif kind == "heading_close":
            heading = None
        elif kind == "blockquote_open":
            quotation = True
        elif kind == "blockquote_close":
            quotation = False
        elif kind == "inline":
            key = heading or ("quote" if quotation else "body")
            content = inline(token, verse=quotation)
            story.append(Paragraph(content, styles[key]))
        elif kind in ("paragraph_open", "paragraph_close"):
            continue
        else:
            raise ResearchError("unsupported_markdown", kind)
    stream = io.BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=PAGE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN + 3,
        title="States Change: Blakean Federalism",
        author="Daniel Ari Friedman",
    )
    doc.build(
        story,
        canvasmaker=partial(Canvas, invariant=1),
        onFirstPage=lambda c, d: footer(c, d.page + 4),
        onLaterPages=lambda c, d: footer(c, d.page + 4),
    )
    return stream.getvalue()


def atlas_pages(spec: ManuscriptSpec, paths: dict[str, Path], start: int) -> bytes:
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=PAGE, invariant=1)
    purposes = (
        (
            "Text and botanical ornament occupy one crafted page. The human-form passage "
            "and distinction between states and individuals support close comparison, "
            "not a literal constitutional blueprint."
        ),
        (
            "The right epigraph distinguishes the person from the present state; the "
            "left names Rahab eternal. The surrounding anti-Deist polemic resists "
            "presenting this page as an already secular charter of tolerance."
        ),
        (
            "Great Eternity and particular form appear above the inscribed diagram. "
            "Reason, Pity, Wrath, This World and Desire must be interpreted within the "
            "page, not converted into government departments."
        ),
        (
            "Los works at an anvil amid text about weapons, kings, limits and provision. "
            "Labor and material consequence complicate an exclusively symbolic account "
            "of passage through states."
        ),
    )
    for index, (image_id, purpose) in enumerate(
        zip(("M32", "J52", "J54", "J73"), purposes, strict=True)
    ):
        asset = next(a for a in spec.assets if a.asset_id == image_id)
        text(
            canvas,
            "Critical plate atlas | " + image_id,
            MARGIN,
            750,
            WIDTH,
            17,
            fontName="Vera-Bold",
        )
        canvas.drawImage(
            ImageReader(io.BytesIO(paths[image_id].read_bytes())),
            MARGIN,
            203,
            width=WIDTH,
            height=519,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
        y = text(canvas, escape(clean(asset.caption)), MARGIN, 187, WIDTH, 9)
        y = text(canvas, purpose, MARGIN, y - 7, WIDTH, 9)
        text(
            canvas,
            'Source: <a href="'
            + escape(asset.rights_url)
            + '">LOC item and Rights &amp; Access</a>. '
            + (
                "Complete provider image; no crop. Historical public-domain work / "
                "item-specific no-known-restrictions advisory; not CC0."
            ),
            MARGIN,
            y - 7,
            WIDTH,
            8,
        )
        footer(canvas, start + index)
        canvas.showPage()
    canvas.save()
    return stream.getvalue()


def render(root: Path, output: Path) -> Path:
    root = root.absolute()
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ResearchError("symlink_output", str(output))
    output = output.absolute()
    if not output.is_relative_to(root / "analysis_output") or ".." in output.parts:
        raise ResearchError("output_boundary", str(output))
    spec_path = safe_path(root, "research/manuscript-inputs.json")
    spec = ManuscriptSpec.model_validate_json(spec_path.read_bytes())
    article = safe_path(root, "docs/manuscript/states-change.md")
    appendix = safe_path(root, "docs/manuscript/references-and-rights.md")
    markdown = article.read_text() + "\n\n" + appendix.read_text()
    paths = validate_manuscript(root, spec, markdown)
    font_directory = fonts()
    front = opening_pages(spec, paths)
    body = body_pages(markdown)
    body_count = len(PdfReader(io.BytesIO(body)).pages)
    atlas = atlas_pages(spec, paths, body_count + 5)
    writer = PdfWriter()
    for data in (front, body, atlas):
        writer.append(io.BytesIO(data))
    for title, page in (
        ("Composition without capture", 0),
        ("Warrants", 1),
        ("Authority", 2),
        ("Counter-models", 3),
        ("Article and references", 4),
        ("Critical plate atlas", body_count + 4),
    ):
        writer.add_outline_item(title, page)
    writer.add_metadata(
        {
            "/Title": "States Change: Blakean Federalism and composition without capture",
            "/Author": "Daniel Ari Friedman",
            "/Subject": f"Private research draft {__version__}",
        }
    )
    pdf = io.BytesIO()
    writer.write(pdf)
    output.mkdir(parents=True, exist_ok=False)
    target = output / f"states-change-blakean-federalism-{__version__}.pdf"
    with target.open("xb") as stream:
        stream.write(pdf.getvalue())
    receipt = {
        "version": __version__,
        "input_schema_version": spec.version,
        "pdf_sha256": digest(target),
        "pages": body_count + 8,
        "front_pages": {str(i): name for i, name in enumerate(spec.fronts, start=1)},
        "body_start_page": 5,
        "body_font_pt": 10,
        "margins_pt": MARGIN,
        "inputs": {
            str(p.relative_to(root)): digest(p)
            for p in (article, appendix, spec_path, *paths.values())
        },
        "font_inputs": {p.name: digest(p) for p in font_directory.glob("Vera*.ttf")},
        "renderer_sha256": digest(Path(__file__)),
        "validator_sha256": digest(safe_path(root, "src/blakean_federalism/manuscript.py")),
        "font_license_sha256": digest(font_directory / "bitstream-vera-license.txt"),
        "manual_visual_review": "pending; this receipt records generation, not acceptance",
    }
    (output / "render-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    (output / "FONT-LICENSE.txt").write_bytes(
        (font_directory / "bitstream-vera-license.txt").read_bytes()
    )
    return target


def main() -> None:
    "Keep the historical helper API; route user-facing rendering through template."
    import sys  # noqa: PLC0415

    from blakean_federalism.cli import app  # noqa: PLC0415

    app(["render-manuscript", *sys.argv[1:]])


if __name__ == "__main__":
    main()
