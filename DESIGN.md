# Blakean Federalism — design contract 0.5.0

The manuscript, original figures and research workbench use black, white and red. Historical Blake reproductions retain their original colours. This contract supersedes the earlier palette, source-selection counts and version labels in the preserved [0.3.0 design research](docs/history/DESIGN-0.3.0.md). That document remains useful for keyboard mechanics, primitives and original research provenance.

## Current palette

| Role | Light | Dark workbench |
|---|---|---|
| Canvas | `#ffffff` | `#000000` |
| Reading surface | `#ffffff` | `#111111` |
| Tonal grouping | `#f2f2f2` | `#222222` |
| Primary text | `#000000` | `#f2f2f2` |
| Secondary text | `#444444` | `#cccccc` |
| Links, highlights and focus | `#b00020` | `#ff6b7f` |
| Rules | `#cccccc` | `#666666` |
| Control boundaries | `#666666` | `#aaaaaa` |

All links and their visible descendants use the red accent. In the web manuscript this includes the template's nested full-size-figure label. The paper uses a white background and black type at every viewport. Existing workbench CSS names `--accent-teal` and `--accent-rust`, and body-figure aliases, are compatibility names for the current red/neutral values; they do not introduce teal or rust into the rendered palette.

## Manuscript and figures

The native docxology/template route produces US Letter pages with 14 mm margins and 10 point body type. The first four physical pages carry the four original graphical abstracts: composition, scholarly disputes, a water decision and source/case evidence. Five further original diagrams develop the body argument. Vector PDF masters and 2200-pixel PNG derivatives accompany the release.

Six uncropped LOC sheets appear within the main text: Milton copy D, leaf 35 (text M32), and Jerusalem copy I, plates 27, 52, 54, 73 and 99. Copy identities, dates and item-level rights remain separate from the fifteen selected ASU quotation records. Historical artwork is proportionally scaled; HTML figure height is automatic, including on mobile. A full-size link opens each source-resolution figure.

## Workbench

The offline workbench has Corpus, Cases and Sources views, embedded Vera fonts and no automatic HTTP retrieval. It displays 180 aggregate cells, ten synthetic alternatives with fifteen checks each, fifteen selected quotation records, six plate metadata records and the current reading ledger. It filters saved queries rather than starting new corpus searches.

Keep source-unit denominators beside results. Distinguish absent queries, measured zero and empty categories. A rule trace exposes its inputs and each result. Detailed source bindings and reading/corpus boundaries remain available in the provenance sections. Online source links require a connection.

Keyboard activation, focus visibility, disclosure controls and mobile reflow retain the earlier interaction contract. The light/dark workbench uses the same visual hierarchy; red is an emphasis or link colour, never a substitute for a textual result.

## Verification

Current author QA is recorded in [rendered-review-0.5.0.json](research/rendered-review-0.5.0.json), with source and qualification epochs in [current-source.json](research/current-source.json). The release evidence binds all 34 reviewed pages, the first-four-page requirement, red anchor descendants, image aspect ratios, desktop/mobile layouts, light/dark workbench states, empty-query behavior and actual restored rendering. The retained earlier blue-label and compressed-portrait controls fail those current browser checks.
