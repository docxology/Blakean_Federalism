# Copyright (c) 2026 Daniel Ari Friedman
"Check labeled manuscript references before invoking a native template renderer."

import re
from collections import Counter
from pathlib import Path

from .models import ResearchError
from .publication_models import ReferenceContract
from .storage import digest, safe_path

KINDS = {
    "definition": "Definition",
    "proposition": "Proposition",
    "axiom": "Axiom",
    "remark": "Remark",
    "theorem": "Theorem",
    "lemma": "Lemma",
    "example": "Example",
}


def manuscript_contract(markdown: str, bibliography: str) -> ReferenceContract:
    "Reject duplicate, missing and manually numbered labels, preserving document order."
    if re.search(r"^\$(?:\s*$| \{#eq:)", markdown, re.MULTILINE):
        raise ResearchError(
            "equation_fence", "Labeled display equations require double-dollar fences"
        )
    keys = [
        match.group(1)
        for match in re.finditer(r"^@\w+\s*\{\s*([^,\s]+)\s*,", bibliography, re.MULTILINE)
    ]
    if not keys or len(keys) != len(set(keys)):
        raise ResearchError("bibliography_identity", "Require unique bibliography keys")
    numbers: dict[str, str] = {}
    counters: Counter[str] = Counter()
    blocks = [
        (match.group(1), match.group(2), match.group(3))
        for match in re.finditer(
            r'^::: \{\.(\w+) #([^\s}]+) title="([^"]+)"\}', markdown, re.MULTILINE
        )
    ]
    openings = re.findall(r"^::: \{[^}]+\}", markdown, re.MULTILINE)
    closings = re.findall(r"^:::\s*$", markdown, re.MULTILINE)
    if len(openings) != len(blocks) or len(closings) != len(blocks):
        raise ResearchError(
            "formalism_fence",
            "Every block requires a supported labeled declaration and closing fence",
        )
    if not blocks:
        raise ResearchError("formalism_missing", "Declare labeled formalism blocks")
    for kind, label, title in blocks:
        if kind not in KINDS or re.match(r"(?:Definition|Proposition|Axiom)\s+\d", title):
            raise ResearchError("formalism_kind", title)
        if label in numbers:
            raise ResearchError("formalism_duplicate", label)
        counters[kind] += 1
        numbers[label] = f"{KINDS[kind]} {counters[kind]}"
    declared = [match.group(1) for match in re.finditer(r"\{#((?:eq|fig|sec):[^\s}]+)", markdown)]
    if len(declared) != len(set(declared)) or set(declared) & set(numbers):
        raise ResearchError("reference_duplicate", "Repeated equation, figure or section label")
    references = set(re.findall(r"(?<![\w/])@([A-Za-z][\w:.-]*)", markdown))
    missing = references - set(keys) - set(declared) - set(numbers)
    if missing:
        raise ResearchError("reference_missing", ", ".join(sorted(missing)))
    return ReferenceContract(
        formalism_numbers=numbers,
        formalism_titles={label: title for _, label, title in blocks},
        bibliography_keys=tuple(keys),
        cited_bibliography_keys=tuple(sorted(references & set(keys))),
        equation_labels=tuple(x for x in declared if x.startswith("eq:")),
        figure_labels=tuple(x for x in declared if x.startswith("fig:")),
        cross_references=tuple(sorted(references - set(keys))),
    )


def source_bindings(root: Path, names: tuple[str, ...]) -> dict[str, str]:
    return {name: digest(safe_path(root, name)) for name in names}
