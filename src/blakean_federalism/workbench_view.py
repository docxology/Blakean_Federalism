# Copyright (c) 2026 Daniel Ari Friedman
"""Server-rendered, escaped evidence records; readable before JavaScript runs."""

import json
from collections.abc import Iterable
from html import escape
from importlib.resources import files
from typing import TYPE_CHECKING

from .manuscript import require_https
from .models import Plane, Role

if TYPE_CHECKING:
    from .workbench_models import Workbench


def text(value: object) -> str:
    return escape(str(value), quote=True)


def link(url: str, label: str) -> str:
    require_https(url)
    return f'<a href="{text(url)}" rel="noopener noreferrer">{text(label)} (online)</a>'


def disclosure(label: str, body: str) -> str:
    return f'<details><summary>{text(label)}</summary><div class="stack">{body}</div></details>'


def coverage_rows(report: "Workbench") -> str:
    queries = {q.query_id: q for q in report.query_groups}
    rows: list[str] = []
    for index, cell in enumerate(report.coverage):
        query = queries[cell.query_id]
        variants = ", ".join(query.variants)
        if cell.source_units:
            values = (
                str(cell.occurrences),
                f"{cell.matched_source_documents} / {cell.source_units}",
                f"{cell.coverage_fraction:.1%}",
            )
        else:
            values = ("N/A", "N/A — no source units", "N/A")
        pairs = (
            ("Plane", cell.plane.value),
            ("Role", cell.role.value),
            ("Occurrences", values[0]),
            ("Matched / units", values[1]),
            ("Coverage", values[2]),
        )
        cells = "".join(
            (
                "".join(
                    (
                        f'<td headers="h-{i} row-{index}">',
                        '<span class="cell-label" aria-hidden="true">',
                        f"{label}</span>{text(value)}</td>",
                    )
                )
            )
            for i, (label, value) in enumerate(pairs)
        )
        rows.append(
            "".join(
                (
                    f'<tr data-query="{text((query.query_id + " " + variants).casefold())}" ',
                    f'data-plane="{cell.plane.value}" data-role="{cell.role.value}"><th ',
                    f'scope="row" id="row-{index}">{text(query.query_id)}<br><span class="meta">',
                    f"{text(variants)}</span></th>{cells}</tr>",
                )
            )
        )
    return "".join(rows)


def case_records(report: "Workbench") -> str:
    records: list[str] = []
    for trace in report.cases:
        record, result = trace.record, trace.assessment
        checks = "".join(
            (
                "".join(
                    (
                        f'<li class="check"><code>{text(check.code)}</code>',
                        '<span class="check-result">',
                        f"{('No violation' if check.passed else 'Violation')}</span>",
                        f"{text(check.detail)}</li>",
                    )
                )
            )
            for check in result.checks
        )
        inputs = disclosure(
            "Inspect actual decision inputs", f"<pre>{text(record.model_dump_json(indent=2))}</pre>"
        )
        outcome = (
            "No stipulated violation"
            if result.admissible_under_proposed_rules
            else "Stipulated violation found"
        )
        ablation = (
            "same programmed assessment"
            if trace.poetic_label_ablation_invariant
            else "assessment changed"
        )
        records.append(
            "".join(
                (
                    '<article class="record"><header class="stack"><h3>',
                    f"{text(record.decision_id)} ",
                    f"· {text(record.alternative)}</h3><p>{text(record.scenario_id)} · ",
                    f"{outcome}</p>",
                    f'</header><p class="meta">All {len(result.checks)} checks are shown. ',
                    "“No violation” can mean that a conditional rule was not triggered; ",
                    "inspect the actual inputs. These are synthetic records, not measured ",
                    f'institutions.</p><ul class="checks">{checks}</ul><p>Poetic/national ',
                    f"label ablation: {ablation}.</p>",
                    f"{inputs}</article>",
                )
            )
        )
    return "".join(records)


def source_records(report: "Workbench") -> str:
    records: list[str] = []
    for quote in report.quotations:
        lines = [
            f'<span class="verse-line">{text(segment.text)}</span>' for segment in quote.segments
        ]
        if quote.quote_id == "Q11":
            verse = (
                '<blockquote class="verse">'
                + "".join(lines[:3])
                + """</blockquote><p class="editorial">Editorial omission between separately
verified excerpts.</p><blockquote class="verse">"""
                + "".join(lines[3:])
                + "</blockquote>"
            )
        else:
            verse = '<blockquote class="verse">' + "".join(lines) + "</blockquote>"
        anchors = "".join(
            f"<li><code>{text(s.anchor)}</code>, occurrence {s.occurrence}</li>"
            for s in quote.segments
        )
        source = link(report.source_urls[quote.asset_id], "Arizona State University transcription")
        anchors_html = disclosure("Inspect transcription anchors", "<ul>" + anchors + "</ul>")
        records.append(
            "".join(
                (
                    f'<article class="record stack"><h3>{text(quote.quote_id)} · ',
                    f"{text(quote.locator)}</h3>",
                    f"{verse}<p>{text(quote.context)}</p><p>{source}</p>{anchors_html}</article>",
                )
            )
        )
    images = "".join(
        (
            "".join(
                (
                    f"<li><strong>{text(a.asset_id)}</strong> — {text(a.caption)}. ",
                    f"{text(a.rights_basis)}. ",
                    f"{text(a.credit)}. {link(a.rights_url, 'Item rights evidence')}</li>",
                )
            )
        )
        for a in report.images
    )
    readings = "".join(
        "".join(
            (
                f"<li><strong>{text(n.source)}</strong>: {text(n.reading_status)}",
                f"{(' · ' + text(n.locator)) if n.locator else ''}",
            )
        )
        + (" · " + link(n.url, "Source") if n.url else "")
        + ("<p><code>" + text(n.sha256) + "</code></p>" if n.sha256 else "")
        + "</li>"
        for n in report.reading
    )
    return (
        "".join(records)
        + """<h3>Image custody and rights</h3><p>Images appear in the manuscript.
This portable workbench embeds no plate images or restricted corpus bodies.</p><ul>"""
        + images
        + "</ul><h3>Reading ledger</h3><ul>"
        + readings
        + "</ul>"
    )


def sections(report: "Workbench") -> dict[str, str]:
    def options(values: Iterable[str]) -> str:
        return '<option value="">All</option>' + "".join(
            f'<option value="{text(value)}">{text(value)}</option>' for value in values
        )

    identity = "".join(
        (
            f"<p>{report.source_units:,} source units · {report.query_count} query ",
            f"groups · {report.stored_occurrences:,} stored query-specific occurrences.</p>",
            f"<p>{report.corpus_pin.unresolved_images} discovered image identifiers ",
            "remain unresolved in the upstream recovery pin. Whole-oeuvre completeness ",
            "is unknown.</p>",
        )
    )
    bindings = (
        "<pre>"
        + text(
            json.dumps(
                {
                    "corpus_pin": report.corpus_pin.model_dump(mode="json"),
                    "inputs": [x.model_dump(mode="json") for x in report.inputs],
                    "producer_sources": report.producer_sources,
                },
                indent=2,
            )
        )
        + "</pre>"
    )
    limits = "<ul>" + "".join("<li>" + text(item) + "</li>" for item in report.limits) + "</ul>"
    return {
        "@@VERSION@@": text(report.producer_version),
        "@@IDENTITY@@": identity,
        "@@PLANES@@": options(plane.value for plane in Plane),
        "@@ROLES@@": options(role.value for role in Role),
        "@@ROWCOUNT@@": str(len(report.coverage)),
        "@@ROWS@@": coverage_rows(report),
        "@@CASES@@": case_records(report),
        "@@SOURCES@@": source_records(report),
        "@@BINDINGS@@": disclosure("Inspect input and producer bindings", bindings),
        "@@LIMITS@@": limits,
        "@@FONTLICENSE@@": text(
            files("blakean_federalism")
            .joinpath("resources/fonts/bitstream-vera-license.txt")
            .read_text()
        ),
    }
