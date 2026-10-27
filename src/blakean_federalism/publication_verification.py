# Copyright (c) 2026 Daniel Ari Friedman
"Verify reference identity and complete selected quotations in actual PDF/HTML bytes."

import io
import json
import re
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from typing_extensions import override

from .manuscript import ManuscriptSpec, normalized
from .models import ResearchError
from .publication_contract import source_bindings
from .publication_models import NativeReceipt, PreparedPublication, ReferenceContract
from .storage import digest, safe_path, write_new

OPENING_PAGE_COUNT = 4


class NumberedBlocks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: dict[str, list[str]] = {}
        self.active: list[str] = []
        self.ids: list[str] = []

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        label = dict(attrs).get("id") or ""
        if label:
            self.ids.append(label)
        if tag == "div":
            self.active.append(label)
            if label:
                self.blocks[label] = []

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self.active:
            _ = self.active.pop()

    @override
    def handle_data(self, data: str) -> None:
        for label in self.active:
            if label in self.blocks:
                self.blocks[label].append(data)


def verify_references(
    contract: ReferenceContract, document: NumberedBlocks, html: str, pdf: str
) -> None:
    for label, number in contract.formalism_numbers.items():
        block = " ".join("".join(document.blocks.get(label, [])).split())
        title = number + " (" + contract.formalism_titles[label] + ")."
        if not block.startswith(title) or number not in pdf:
            raise ResearchError("rendered_formalism", label)
    if len(document.ids) != len(set(document.ids)):
        raise ResearchError("rendered_duplicate_id", "HTML identifiers must be unique")
    for key in contract.cited_bibliography_keys:
        if "ref-" + key not in document.ids:
            raise ResearchError("rendered_bibliography", key)
    for label in (*contract.equation_labels, *contract.figure_labels):
        if label not in document.ids:
            raise ResearchError("rendered_reference", label)
    if any(token in html or token in pdf for token in ("[@", "[?]", "??", "citation-not-found")):
        raise ResearchError("rendered_unresolved", "Unresolved reference in actual edition")


def verify_opening(pages: list[str]) -> None:
    if len(pages) <= len((1, 2, 3, 4)) or "States Change" not in pages[0]:
        raise ResearchError("rendered_opening", "Cover absent")
    for index in (1, 2, 3):
        if f"Graphical abstract {index + 1}" not in pages[index]:
            raise ResearchError("rendered_opening", f"Physical page {index + 1}")


def verify_opening_images(reader: PdfReader, figures: Path) -> None:
    """Verify each actual opening illustration, not merely its page heading."""
    if len(reader.pages) < OPENING_PAGE_COUNT:
        raise ResearchError("rendered_opening_image", "Four physical pages required")
    for index in range(OPENING_PAGE_COUNT):
        with Image.open(safe_path(figures, f"abstract-{index + 1}.png")) as original:
            expected = original.convert("RGB")
            pixels = expected.tobytes()
            size = expected.size
        matched = False
        for embedded in reader.pages[index].images:
            with Image.open(io.BytesIO(embedded.data)) as actual:
                if actual.size == size and actual.convert("RGB").tobytes() == pixels:
                    matched = True
                    break
        if not matched:
            raise ResearchError("rendered_opening_image", f"Physical page {index + 1}")


def verify_notation(pages: list[str], html: str) -> list[int]:
    """Require the actual notation table before the numbered argument in both editions."""
    start = html.find('id="sec:notation"')
    body = html.find('id="sec:s1"')
    table = html.find("<table", start)
    end = html.find("</table>", table)
    if start < 0 or body <= start or not (start < table < end < body):
        raise ResearchError(
            "rendered_notation", "Front notation table absent or after the argument"
        )
    if "Symbol" not in html[table:end] or "Meaning" not in html[table:end]:
        raise ResearchError("rendered_notation", "Notation table headings are missing")
    found = [
        i + 1
        for i, page in enumerate(pages)
        if "Notation and reading conventions" in page and "Symbol" in page and "Meaning" in page
    ]
    if len(found) != 1 or found[0] not in (5, 6, 7):
        raise ResearchError(
            "rendered_notation", "Notation must appear in the physical front matter"
        )
    return found


def verify_publication(root: Path, stage: Path) -> dict[str, object]:
    prepared = PreparedPublication.model_validate_json(
        safe_path(stage, "prepared-publication.json").read_bytes()
    )
    if prepared.inputs != source_bindings(root, tuple(prepared.inputs)):
        raise ResearchError("publication_source_changed", "Sources differ from the consumed stage")
    native = NativeReceipt.model_validate_json(
        safe_path(stage, "native-render-receipt.json").read_bytes()
    )
    if (
        native.template_commit != prepared.template.commit
        or native.template_repository != prepared.template.repository
        or native.writer_calls != prepared.template.writers
    ):
        raise ResearchError("template_identity", "Native receipt differs from the selected engine")
    for name, expected in native.resolved_inputs.items():
        if digest(safe_path(stage, name)) != expected:
            raise ResearchError("native_input_changed", name)
    for name, expected in prepared.figures.items():
        if digest(safe_path(stage, "output/figures/" + name)) != expected:
            raise ResearchError("publication_figure_changed", name)
    for name, expected in native.outputs.items():
        if digest(safe_path(stage, name)) != expected:
            raise ResearchError("native_output_changed", name)
    pdf = PdfReader(safe_path(stage, native.pdf))
    pages = [page.extract_text() or "" for page in pdf.pages]
    pdf_text = unicodedata.normalize("NFKC", " ".join(" ".join(pages).split()))
    html = safe_path(stage, native.html).read_text()
    document = NumberedBlocks()
    document.feed(html)
    verify_references(prepared.contract, document, html, pdf_text)
    verify_opening(pages)
    verify_opening_images(pdf, safe_path(stage, "output/figures/abstract-1.png").parent)
    notation_pages = verify_notation(pages, html)
    aux = safe_path(stage, "output/pdf/_combined_manuscript.aux").read_text()
    pdf_keys = {match.group(1) for match in re.finditer(r"\\bibcite\{([^}]+)\}", aux)}
    if pdf_keys != set(prepared.contract.cited_bibliography_keys):
        raise ResearchError("pdf_bibliography", "Compiled PDF bibliography keys differ from source")
    spec = ManuscriptSpec.model_validate_json(
        safe_path(root, "research/manuscript-inputs.json").read_bytes()
    )
    expected = Counter(unicodedata.normalize("NFKC", normalized(q.text)) for q in spec.quotations)
    missing = [
        q.quote_id
        for q in spec.quotations
        if pdf_text.count(unicodedata.normalize("NFKC", normalized(q.text)))
        != expected[unicodedata.normalize("NFKC", normalized(q.text))]
    ]
    if missing:
        raise ResearchError("rendered_quotation", ", ".join(missing))
    result: dict[str, object] = {
        "pages": len(pages),
        "notation_physical_pages": notation_pages,
        "verified_quotations": len(spec.quotations),
        "formalism_numbers": prepared.contract.formalism_numbers,
        "equation_labels": prepared.contract.equation_labels,
        "figure_labels": prepared.contract.figure_labels,
        "resolved_bibliography_keys": prepared.contract.cited_bibliography_keys,
        "front_physical_pages": [1, 2, 3, 4],
        "outputs": native.outputs,
        "template_commit": native.template_commit,
        "scope": (
            "Content/reference verification only; visual/browser review and "
            "independent acceptance remain separate"
        ),
    }
    write_new(stage / "rendered-content-verification.json", json.dumps(result, indent=2) + "\n")
    return result
