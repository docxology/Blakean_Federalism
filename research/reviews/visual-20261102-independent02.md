# Independent final02 review

**REQUEST_CHANGES for the frozen source candidate. PDF/HTML working-draft review: PASS_WITH_LIMITATIONS.**

The source blocker is narrow: `work/entomology/tests/test_research_figures.py` grew from 226 to **255 nonblank, noncomment lines** (299 physical lines), without a SIZE_OK exception. The applicable programming skill explicitly calls a module above 250 pure lines a defect, including tests. Split this test module while preserving its tests and rejecting cases; separately qualify the new source/test identity. This finding does not require changing or rerendering the inspected manuscripts. No candidate file was edited by this auditor.

## Exact scope and bindings

The caller-held `coordination/FROZEN-REVIEW-INPUTS.json` SHA-256 is `3e662a5fe7d6e733d55315921d6750c642af4c482255ca4de0c374dc2aa2bfa6`. All **1,551 members** matched at initial admission and final revalidation. The final revalidation is in `final-input-verification.json`. This verdict concerns only that frozen candidate, not a later correction.

| Edition | PDF SHA-256 | HTML SHA-256 | Physical pages |
|---|---|---|---|
| Entomology 0.8.0 | c0a86f1249b741d19363d325d47a87bf0516de9a8152128ba962b238fd3cad74 | 90fb1170c301590f46a4dffae53133dd347aebcbae2859d41cce81b9a291910f | 45 |
| Federalism 0.19.0 | ece2d8d6d11030eb654e5bf287387c9f580801827e40f9f2d6d79e6ac7f4f136 | 8c5f32b191b85c7b2724744cb71dc2667719a1a4331f77156f81a78e6e42b7ae | 79 |

Exact paths and native receipt identities are in `VERDICT.json`. Public SDK identity remains Blake 0.7.0 at `263d7c83abe6f1309a64af3285a683c1b7672269`; template source remains `efce6d6f5b3c4e8e2bbf92d8250855a0a9389ae8`.

## Evidence and binary observations

All command names below refer to this review's `commands/` directory unless prefixed by the parent packet. Each directory retains exact argv/environment, prelaunch, PID, raw stdout/stderr and completion. Image inspection observations are recorded separately in `visual-observations.json`.

| Scenario and invocation | Binary observable | Captured artifact |
|---|---|---|
| Guidance and external runtime intake, exact supplied logged Python command; commands000–007 | Both Python prefixes resolve on GitVault; guidance read before the completion marker | `GUIDANCE_COMPLETE`, `commands/000-guidance/` through `007-guidance-complete/` |
| Frozen SHA/member verification, commands010 and036 | Manifest pin matches; 1,551/1,551 members match; final mount check true | `initial-input-verification.json`, `final-input-verification.json` |
| Normal installed source and SDK byte inspection, command011 | 44 E package members and 163 SDK members match their recorded pins; F installed package and same163 SDK members match | `commands/011-bindings-delta/stdout.log`, `installed-source-delta.json` (installed section only) |
| Baseline source comparison, command015; removed-member check025 | F program bytes unchanged; E generic/domain boundary retained; E obsolete publication_relations.py removed | `verified-delta.json`, `entomology-verified-diff.txt`, `federalism-verified-diff.txt`, `commands/025-software-evidence-corrected/stdout.log` |
| Review actual installed suite/typing/lint/format producer records, commands024–025 | Owner suite reports464 passing; recomputed coverage2782/3064=90.7963% application,1012/1503=67.3320% tools; typing0 diagnostics; Ruff passes | `procedure-review.json`; parent `evidence/135-qualified-installed-regression/`, `119-final-types-after-split/`, `160-final-lint-and-format/`, `161-final-format-readback/` |
| Native writer-procedure review, commands024–027 | Both real pinned template writer calls recorded, normal completion and matching output pins | Parent `evidence/142-entomology-native-final-admission/`, `143-entomology-native-final/`, `095-federalism-native-admission/`, `096-federalism-native-inner/`; exact native receipts |
| Fresh Poppler rasterization: `pdftoppm -r 72 -png PDF PREFIX`, commands13–14; all124 physical-page overview inspection | 45+79 rasters produced; every page visually inspected; no observed missing page, overlap or clipping; contents starts physical5 in both | `*-page-NN.png`, `*-sheet-NN.png`, `page-sheet-map.json`, `visual-observations.json` |
| Actual installed PDF reader on both frozen PDFs, command023 | Titles Blakean Entomology / States Change;45/79 pages; deliberately wrong title rejected as pdf_title | `independent-controls.json`, `entomology-pdf-readers/`, `federalism-pdf-readers/`, `wrong-title-control/` |
| Source/image joins and negative controls through installed API, command023 | Three exact ordered XML quotations match; original image bytes equal aliases; fabricated quote and corrupt-image copy rejected | `independent-controls.json`, `corrupt-image-control/` |
| Fresh owned Chromium at1440 and390px, `bun browser-check.mjs PACKET OWNED`, command018 | E18/F37 images loaded with natural proportions; E74/F265 MathJax containers;0 math errors, missing anchors or duplicate IDs; in-memory dangling anchor detected in both documents | `browser/*-dom.json`, `browser/*-negative-control.json`, `browser/RESULT.json`,110 fresh figure screenshots, `browser/CLOSED.json` |
| Real horizontal wheel on E table2 at both widths, `bun wheel-check02.mjs PACKET OWNED`, command033 | ScrollLeft0→300; caption x unchanged; document width contained; browser closed normally | `browser/wheel02-1440.json`, `wheel02-390.json`, matching PNGs, `WHEEL02-CLOSED.json` |
| Unchanged corpus/vocabulary/decision identities and changed module counts, commands034–035 | Original pinned inputs unchanged; production modules ≤233 pure lines; changed test module255 violates hard ceiling | `data-shape-review.json`, `commands/035-test-module-shape/stdout.log` |

The software suite was **not rerun** by this auditor. The current E result is supported by inspected raw owner execution and directly checked installed bytes. F's818-test result remains the previous producer's qualification; the program-byte comparison and normal installed equality were independently checked, without relabelling that suite as fresh.

## Physical and browser findings

I viewed every physical PDF page through22 labelled six-page sheets generated independently from the frozen PDFs, then viewed E physical pages2,3,4,9,10 singly. All three selected original images were opened at enlarged resolution. E has the authentic cover on1, three distinct illustrated arguments on2–4, contents on5. F retains opening composition on1 and graphical pages2–4, contents on5, front notation on6–7 and the shortened abstract on8. Native figures, tables, equations, bibliography and reading-boundary appendices remain visibly present. This is layout/selection review, not word-by-word critical-edition collation.

The new E panels preserve complete captured image boundaries and proportion. Fly's reciprocal questions do not become insect cognition; Dream's offered route does not become narrated arrival; Thel's infant comparison does not become a worm clade. The three exact XML selections are SongsY40.07–10, SongsY26.19–22 and ThelF06.03–04. The p9 table distinguishes names, compounds, verbs, analogy and conditional biological leads. The p10 tree explicitly excludes sequence and linguistic ancestry. The47 reviewed/35,992 unreviewed denominator and Baine's unavailable/unread chapter remain explicit. No adjudication or taxonomic identification was added. F's revised abstract and captions retain stipulated safeguards, finite families, person-specific conditions and unassessed practical premises rather than turning calculated conjunctions into legitimacy.

All110 owner screenshots were independently hashed in `owner-browser-bindings.json`; four were visually opened. One owner mobile Thel screenshot is blank beneath the heading, consistent with a transition-frame capture. The fresh independent mobile03 screenshot displays the full figure and caption. The blank owner frame remains preserved and is not used as positive visual evidence. Fresh all-image DOM measurement and110 fresh figure captures supplement the full PDF inspection. Only the explicitly listed browser screenshots in `visual-observations.json` were visually opened; screenshot capture is not claimed as visual reading of every captured frame. Mobile figure labels remain small at inline size, with full-size links and real caption text. Keyboard/assistive-technology operation is not certified.

## Preserved audit failures and exclusions

- Command011 used the wrong baseline comparison root and therefore overstated changes. Its installed-byte verification is valid; its delta portion and the first diff files are diagnostic only. Command015 uses the actual baseline/source directories and supersedes that delta.
- Command024's coverage summarizer assumed tools paths were absolute and raised ZeroDivisionError. No zero denominator was accepted. Command025 reruns the relevant procedure review using the actual relative tools paths and recomputes both complete fractions.
- Command031's wheel harness assumed document width equalled viewport width. Desktop Chrome reserves15px for the scrollbar, so1425≠1440 failed despite actual wheel movement. The first browser closed normally. Command033 reruns both desktop/mobile cases with the correct containment assertion and retains fresh screenshots and normal closure.
- The prior independent-final01 setup-only attempt remains unqualified. No earlier failure or source epoch is retroactively accepted.

The accepted output scope excludes specialist Blake scholarship, whole-oeuvre/image-corpus reading, anatomical identification, new contextual adjudication, item-level rights clearance, assistive technology/accessibility certification, offline MathJax, hosted CI and release. Canonical integration, private-main push, remote readback and Downloads delivery remain root-owned separate events. No lease, installation, acquisition, Git action or manuscript renderer was run by this auditor.

The review is terminal for this frozen input. `VERDICT.json` preserves the source blocker separately from the bounded PDF/HTML pass. `EVIDENCE-MANIFEST.json` closes the settled review artifacts; its own file and the final manifest-writing command spool are explicitly excluded from recursive self-hashing.
