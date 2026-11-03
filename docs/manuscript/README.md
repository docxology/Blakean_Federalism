# Published manuscript and new native production

Read the [published PDF](../../Blakean_Federalism.pdf),
[project status](../PROJECT_STATUS.md), [authoring conventions](../style-guide.md)
and [public reproduction profile](../public-reproduction.md) before changing an
input. The public [publication record](../../publication.json) binds the selected
edition. Current source maintenance and the original native producer are distinct.

## Published 1.0.0 edition

The current stage is `analysis_output/publication/doi-review-native-1.0.0-20261103-01`:
76 pages, a real DOI on the cover, and three expanded graphical abstracts
after its cover diagram. Contents begin on physical page 5. Geometry is
`letterpaper,margin=11mm,footskip=4mm`, with unchanged 10-point body type.
The actual pinned PDF/web writers run through the normal-installed Python 3.15.1
host and separate Python 3.14 template environment. Forty quotation records,
thirty-three body figures, formal numbering, bibliography and source bindings
have real native content verification. [Current qualification](../../research/review-candidate-1.0.0.json)
records independent output and canonical consumer checks separately.

The scene cards combine exact quotations, reading locators and questions; the
institutional graphic makes all four assessment steps explicit; the corpus
graphic adds actual leave-one-family frequency ranges. Fresh workbench production
preserves counts and domain records. Four one-unit floating-point HHI changes
between Python 3.11 and 3.15 remain explicit and rational-oracle checked; old/new
reports are preserved, not presented as byte-identical. A producer-version guard
rejects a forged sidecar, while historical audit report/receipt hashes stay fixed.
The earlier 79-page editorial edition keeps its own producer and acceptance.

The [publication guide](../publication-plan.md) records author-approved public
distribution; [publication facts](../../publication.json) bind the deposited bytes.

The deposited rendering-input archive preserves the exact original native
metadata, including its then-private status. Those captured inputs do not
describe current GitHub visibility. Use the archive and its verifier when
inspecting the published production; do not relabel an old native receipt
after changing source.

## Current source and runtime contract

The installed `blakean render-manuscript` command is the supported entry point.
It prepares source-bound inputs and invokes the actual pinned template
`PDFRenderer.render_combined` and `WebRenderer.render_combined` writers through
`tools/template_render.py`. There is no alternate body renderer in active source.

Blake owns corpus custody and reusable algorithms. Federalism owns source
selection, political and institutional policy, interpretation, domain figures
and front matter. The exact SDK is selected in `pyproject.toml` and `uv.lock`;
the independent template pin is
`efce6d6f5b3c4e8e2bbf92d8250855a0a9389ae8`.
Use the normal Python 3.15.1 host and the separately qualified Python 3.14
template environment. Verify both runtime prefixes on mounted GitVault and
bind TMPDIR, TMPPREFIX, caches and TeX output externally. Keep the complete
authorized retained fixtures; a public source-only clone cannot run the full
analytical/native workflow.

## Generate a new native epoch

Use the supported repository lease and external CPython/runtime/cache roots.
Generate the concordance explicitly before passing it to the renderer;
choose new output names for later runs. Both commands use the already qualified
corpus, keeping saved query and corpus pins unchanged:

```bash
BLAKE_RENDER_EPOCH=native-new
uv run --locked --no-sync blakean analyze \
  --corpus local_data/corpus/blake-v0.2.0-qualified \
  --pin research/corpus-pin.json --queries research/queries.json \
  --output "analysis_output/$BLAKE_RENDER_EPOCH/concordance.json"
uv run --locked --no-sync blakean render-manuscript \
  --template-root "$BLAKE_TEMPLATE_ROOT" --template-python "$BLAKE_TEMPLATE_PYTHON" \
  --corpus local_data/corpus/blake-v0.2.0-qualified \
  --concordance-file "analysis_output/$BLAKE_RENDER_EPOCH/concordance.json" \
  --readings research/scholarship-reading-0.13.0.json \
  --output "analysis_output/publication/$BLAKE_RENDER_EPOCH"
```

Bind the template variables to the clean pinned worktree and its external
compatible interpreter recorded in the native receipt. Canonical template drift
does not change that recorded renderer origin. Choose a new output epoch;
preserve earlier native files, failures and logs. The retained 2026-10-28
static HTML qualification includes a missing-asset rejection control.
Current browser and MathJax acceptance require their own output-bound record.

The template checkout must be clean and exactly match the recorded source.
Preparation verifies quotation selections, source identities, original
concordance spans and producer bindings before output. Missing/malformed
inputs, changed source, unsupported profiles and occupied destinations refuse.
Failure logs and partial epochs remain retained. A completion receipt follows
successful output verification; it grants no visual or scholarly acceptance.

## Authoring and output acceptance

Use stable section, figure, table, equation and formalism identifiers. Native
filters own counters and cross-references; [the style guide](../style-guide.md)
defines the authored grammar. Keep one unnumbered References location and
complete BibTeX. Do not introduce a second numbering or bibliography engine.

Inspect every changed physical page and the complete HTML at actual desktop
and mobile widths. Verify resolved title/DOI metadata, quotations, citations,
formal numbering, image proportions, table overflow and output hashes.
MathJax uses the template's network profile; a self-contained evidence
workbench is a separate output. Functional browser checks, accessibility,
scientific criticism, item-level rights and release acceptance remain distinct.

Run installed software checks and separate 90% application / 60% infrastructure
statement-and-branch floors from the [verification instructions](../../README.md#verification).
A changed source, input, method, stage or native output needs a new epoch and
appropriate independent review. No old one-shot native grant renews itself.

## Retained qualifications

The [preceding guide](../../research/history/documentation-maintenance-20261103-preimage/docs/manuscript/README.md)
retains the original chronological instructions and exact former qualification
claims. Earlier papers, source maps, source overlays, print paths and failed
native attempts remain attached to their own producers. The
[published installation](../../research/publication-20261103.json) and
[post-release maintenance qualification](../../research/methods-retirement-20261103.json)
do not replace the [1.0.0 native/output qualification](../../research/review-candidate-1.0.0.json).

See [maintenance and custody](../maintenance.md) for branch/worktree retention.
