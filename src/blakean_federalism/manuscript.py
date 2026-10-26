# Copyright (c) 2026 Daniel Ari Friedman
"""Verify manuscript quotations and selected assets before rendering any output."""

import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field
from typing_extensions import override

from .models import Digest, FrozenModel, ResearchError
from .storage import verify_file


class Asset(FrozenModel):
    asset_id: str
    path: str
    url: str
    sha256: Digest
    size: int = Field(gt=0)
    kind: Literal["html", "image", "rights"]
    caption: str = ""
    rights_basis: str = ""
    credit: str = ""
    rights_url: str = ""


class Segment(FrozenModel):
    anchor: str
    occurrence: int = Field(ge=0)
    text: str = Field(min_length=1)


class Quotation(FrozenModel):
    quote_id: str
    asset_id: str
    locator: str
    segments: tuple[Segment, ...] = Field(min_length=1)
    context: str

    @property
    def text(self) -> str:
        return "\n".join(segment.text for segment in self.segments)


class ManuscriptSpec(FrozenModel):
    version: Literal["0.2.0", "0.5.0", "0.6.0", "0.7.0", "0.8.0"]
    assets: tuple[Asset, ...]
    quotations: tuple[Quotation, ...]
    fronts: tuple[str, ...]


class VerseParser(HTMLParser):
    """Read selected ASU anchor lines, excluding small editorial locator/footnote type.

    Retain original spelling and punctuation. Only whitespace is normalized. Column
    epigraphs require explicit anchor segments; this does not collate illuminated copies.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lines: dict[str, list[str]] = {}
        self.anchor: str | None = None
        self.parts: list[str] = []
        self.font_depth: int = 0
        self.suppressed: int | None = None
        self.sup_depth: int = 0

    def finish(self) -> None:
        if self.anchor is not None:
            text = " ".join("".join(self.parts).split())
            self.lines.setdefault(self.anchor, []).append(text)
        self.anchor = None
        self.parts = []

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "br":
            self.finish()
        if tag == "a" and re.search(r";E\d+", attributes.get("name") or ""):
            self.finish()
            self.anchor = attributes["name"]
        if tag == "font":
            self.font_depth += 1
            if attributes.get("size") == "-2" and self.suppressed is None:
                self.suppressed = self.font_depth
        if tag == "sup":
            self.sup_depth += 1

    @override
    def handle_endtag(self, tag: str) -> None:
        if tag == "font":
            if self.font_depth == self.suppressed:
                self.suppressed = None
            self.font_depth -= 1
        if tag == "sup":
            self.sup_depth -= 1
        if tag == "p":
            self.finish()

    @override
    def handle_data(self, data: str) -> None:
        if self.anchor is not None and self.suppressed is None and self.sup_depth == 0:
            self.parts.append(data)


def normalized(text: str) -> str:
    return " ".join(text.split())


def require_https(url: str) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or "\\" in url
        or any(char.isspace() for char in url)
    ):
        raise ResearchError("source_url", "A credential-free HTTPS source URL is required")


def validate_manuscript(root: Path, spec: ManuscriptSpec, markdown: str) -> dict[str, Path]:
    """Reject changed sources, ambiguous IDs, unverified quotations and missing rights."""
    if spec.fronts != ("composition", "warrants", "authority", "countermodels"):
        raise ResearchError("front_pages", "Four explicit physical opening pages are required")
    expected_images = {
        "0.2.0": {"M32", "J52", "J54", "J73"},
        "0.5.0": {"M32", "J52", "J54", "J73", "J27", "J99"},
        "0.6.0": {"M32", "J52", "J54", "J73", "J27", "J99", "J55", "J91", "J12", "J61"},
        "0.7.0": {"M32", "J52", "J54", "J73", "J27", "J99", "J55", "J91", "J12", "J61"},
        "0.8.0": {"M32", "J52", "J54", "J73", "J27", "J99", "J55", "J91", "J12", "J61", "J59"},
    }[spec.version]
    if {a.asset_id for a in spec.assets if a.kind == "image"} != expected_images:
        raise ResearchError("image_set", "The exact selected plate set is required")
    paths: dict[str, Path] = {}
    sources: dict[str, VerseParser] = {}
    for asset in spec.assets:
        if asset.asset_id in paths:
            raise ResearchError("duplicate_asset", asset.asset_id)
        require_https(asset.url)
        path = verify_file(root, asset.path, asset.size, asset.sha256)
        paths[asset.asset_id] = path
        if asset.kind == "image" and not all(
            value.strip()
            for value in (asset.caption, asset.rights_basis, asset.credit, asset.rights_url)
        ):
            raise ResearchError("image_rights", asset.asset_id)
        if asset.kind == "image":
            require_https(asset.rights_url)
        if asset.kind == "html":
            parser = VerseParser()
            parser.feed(path.read_text(encoding="utf-8"))
            parser.finish()
            sources[asset.asset_id] = parser
    expected: Counter[str] = Counter()
    identifiers: set[str] = set()
    for quote in spec.quotations:
        if quote.quote_id in identifiers or quote.asset_id not in sources:
            raise ResearchError("quotation_identity", quote.quote_id)
        identifiers.add(quote.quote_id)
        for segment in quote.segments:
            candidates = sources[quote.asset_id].lines.get(segment.anchor, [])
            if segment.occurrence >= len(candidates) or (
                candidates[segment.occurrence] != segment.text
            ):
                raise ResearchError("quotation_mismatch", quote.quote_id + ":" + segment.anchor)
        expected[normalized(quote.text)] += 1
    blocks = (m.group(0) for m in re.finditer(r"(?:^>[^\n]*(?:\n|$))+", markdown, re.MULTILINE))
    actual = Counter(
        normalized(
            re.sub(r"\\\n", "\n", re.sub(r"^> ?", "", block, flags=re.MULTILINE)).replace(
                "\\'", "'"
            )
        )
        for block in blocks
    )
    if actual != expected:
        raise ResearchError("manuscript_quotation", "Blockquotes differ from verified ledger")
    return paths
