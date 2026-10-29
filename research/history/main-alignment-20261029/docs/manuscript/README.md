# Rebuild the current private manuscript

The current edition uses public SDK `d020f47767996a061b6f60e93a82da9386a7926c` and a fresh locked noneditable
installation: 655 tests pass, with 92.30% application and 70.72% tool branch-aware
coverage. Strict typing, Ruff and dependency compatibility pass; all four
historical analytical JSON files replay byte for byte. The actual pinned native
template writers produced the 72-page PDF and HTML at
`analysis_output/publication/expansion-20261028-02`. This fresh PDF is empirically byte-identical
to the preceding 72-page edition.

The person-specific procedural comparison retains fourteen procedures,
twenty-eight claimants, explicit unmet requirements and partial-order
incomparability. Its two figures stay in the main argument. The political
requirements are application policy; no generic composition statistic is used
as an institutional legitimacy score. See
[current qualification](research/expansion-installed-20261028.json) and the
[render guide](docs/manuscript/README.md). Independent review and browser behavior
have separate scopes.

Use the supported repository lease and external CPython/runtime/cache roots.
The exact current command supplies the already qualified corpus and a fresh
replayed concordance explicitly; it does not rely on a stale default filename:

```bash
uv run --locked blakean render-manuscript \
  --template-root "$BLAKE_TEMPLATE_ROOT" --template-python "$BLAKE_TEMPLATE_PYTHON" \
  --corpus local_data/corpus/blake-v0.2.0-qualified \
  --concordance-file analysis_output/expansion-installed-replay-20261028-01/concordance.json \
  --readings research/scholarship-reading-0.13.0.json \
  --output analysis_output/publication/native-new
```

Bind the template variables to the clean pinned worktree and its external
compatible interpreter recorded in the native receipt. Canonical template drift
does not change that recorded renderer origin. Choose a new output epoch;
preserve earlier native files, failures and logs. Static HTML asset and fragment
checks passed with a missing-asset rejection control; browser/MathJax behavior
was not tested in this pass.

## Retained version-specific authoring and historical qualifications

Version 0.16.0 uses the actual PDF and HTML rendering infrastructure from a clean, commit-pinned checkout of [docxology/template](https://github.com/docxology/template). The pin, writer identities and citation profile are recorded in `research/template-rendering.json`. The canonical authoring files are `states-change.md`, `references-and-rights.md`, `references.bib`, `config.yaml` and `preamble.md`.

The project uses its external Python 3.11 environment for preparation and verification. The pinned template uses a separately supplied compatible external Python environment. Verify both `sys.prefix` and `sys.base_prefix` for each environment, the mounted GitVault volume, external TMPDIR/cache bindings and the supported repository admission before execution. Dependencies include Pandoc, compatible pandoc-crossref, XeLaTeX, BibTeX and Poppler. Install the optional manuscript dependencies explicitly when provisioning; do not replace an active environment implicitly.

~~~bash
uv run python -m tools.acquire_manuscript
uv run blakean render-manuscript \
  --template-root "$TEMPLATE_REPO_ROOT" \
  --template-python "$TEMPLATE_PYTHON" \
  --output analysis_output/publication/new-run
~~~

The template checkout must be clean and exactly match the recorded commit. Rendering invokes `PDFRenderer.render_combined` and `WebRenderer.render_combined` after the template's manuscript injection, without a substitute body renderer. `tools/render_manuscript.py` forwards to this command; its older helper API remains for historical compatibility tests. A source checkout is needed for the native worker. The core wheel still supports the separate offline evidence workbench without the optional PDF stack.

Acquisition recovers 22 individually hash-pinned inputs: 6 ASU HTML texts, 14 LOC JPEGs and 2 item metadata/rights responses. Existing valid files are retained. Changed bytes, unsafe paths, symlinks and unapproved hosts fail. A changed provider page requires a reviewed new source epoch. The larger recovered corpus is a separate local custody object under `PRIVACY.md` and `corpus-pin.json`. Modern scholarly PDFs remain local and ignored.

Preparation revalidates the copied index, every stored concordance span, the quotation selection and source hashes before creating a new stage inside `analysis_output`. Occupied outputs are refused. A completion receipt is written only after the native PDF and HTML outputs pass their content and identity checks. A failed stage and its native log remain inspectable. Rendering never grants its own visual or scholarly acceptance.

Layout is US Letter with 14 mm margins and 10 point body type. Four graphical abstracts occupy physical pages 1–4, followed by contents, notation and the article. Eighteen original diagrams have vector PDF masters and high-resolution PNG derivatives. Fourteen uncropped LOC sheets appear beside their readings with item-specific credits and dates. The 0.11.0 selection adds the Jerusalem frontispiece and final plate, retaining full provider images and orientation. The four graphical abstracts use original plates and italic serif quotations. Bitstream Vera and DejaVu serif licenses accompany the embedded figure fonts. Nineteen labeled formalisms, thirteen labeled equations and 60 cited references use native numbering and bibliography controls. All Blake block quotations use an italic quote environment in PDF, an italic blockquote in HTML and italic verse cards in the workbench; source text remains independently checked.


Author formalisms as fenced Divs, for example `::: {.definition #def:typed title="Four typed sorts"}`, closed by `:::`. Refer to them with `[@def:typed]`. Counters are automatic within each kind. Equations use a display-math block followed by `{#eq:name}` and references `[@eq:name]`. Figures have `{#fig:name}` identifiers. Scholarly citations use `[@key, p. 17]` and an entry in `references.bib`; PDF uses natbib/BibTeX and HTML uses citeproc. The source validator rejects duplicate identifiers, unsupported or unclosed formalism blocks, unresolved references and manually numbered formalism titles. Normative axioms are explicitly proposed commitments; the propositions establish only the stated formal consequences.

The verifier checks source and figure hashes, separate output identities, the correct embedded illustration on each of physical pages 1–4, actual HTML formalism headings, bibliography identifiers, compiled PDF citation keys, and the multiplicities of 40 selected Blake quotation records (156 exact segments). It strips Markdown hard-line-break, escaped straight-apostrophe and escaped-hyphen syntax before quotation comparison. Escaping a straight apostrophe makes Pandoc emit a literal quote glyph rather than letting XeLaTeX apply a typographic substitution. The captured source spelling and punctuation remain exact. This is selection verification, not critical-edition collation. SOURCE_DATE_EPOCH and UTC are fixed, but byte-identical native rerendering is a separate empirical check rather than an assumed guarantee.

The paper HTML uses the template's network MathJax profile. Its formulas need that CDN to typeset in a fresh browser. The research workbench remains a separate self-contained offline artifact. A rendering bundle can reproduce the bounded paper from included selected inputs; it is not full analytical reproduction or permission to redistribute the entire corpus.

Qualification uses real files, PDFs, images and subprocesses:

~~~bash
uv run pytest tests -q --cov=blakean_federalism --cov=tools --cov-branch --cov-report=term-missing
uv run basedpyright
uv run ruff check src tests tools
uv run ruff format --check src tests tools
~~~

Application coverage must remain at least 90 percent and infrastructure at least 60 percent; read both totals from the per-file report, since one combined floor cannot express two separate targets. The top-level README command enforces the application floor with its `--cov-fail-under` value. Inspect every final PDF page and the live HTML separately; text extraction alone cannot establish layout quality. Bind the QA record to the actual output hashes. The repository and release remain private; no public Zenodo deposit or blanket corpus-image redistribution is authorized.

The CLI render-manuscript command is the publication entry point. tools/render_manuscript.py retains the original bootstrap controls; the pinned native template defines the current publication profile.


The front notation source is notation.md. Preparation includes its hash and places 01_notation.md after the opening abstracts/contents and before the article. Native verification requires a real notation table before the numbered argument in HTML and in physical front matter in the PDF. The table separates relation C from coverage C_q; Jac, Pr and Lift name the corpus association measures. All eighteen diagrams are regenerated from code; corpus statistics and finite intervention results retain their original analytical producers. Serialized Measure values now reject inconsistent rate/coverage denominators before a chart consumes them.

The 0.14.0 opening figures use data-bound analytical layouts. The cover retains an uncropped Jerusalem frontispiece and two verified verse excerpts. Pages 2-4 devote their image area to a passage/reading/test table, an essential-intervention matrix and a relative source-sensitivity plot. The PDF cover caption is injected through the native preamble from the same caption source as the HTML cover. The previous illuminated layouts remain available for their recorded producer versions.

Version 0.15.0 starts the fourth abstract with the matched forms, counted words and a worked frequency calculation. Its two columns show separate weighting choices. The six passage rows and five conflict rows use direct questions and named changes. The current opening paragraph and subsections connect those figures to the scholarly argument. Earlier releases preserve their original sources and figure masters.


## Current 0.16.0 rendered qualification

The frozen stage is `analysis_output/publication/shared-methods-domain-0.16-05`:
69 PDF pages, 40 selected quotation records, 19 formalisms, 13 equations and 60
cited references. Eighteen project-authored designs plus fourteen pinned plates
produce 32 HTML image instances: 28 numbered body/plate figures and four opening
abstracts. The local review notation has ten rows on its own page. The contents
retain 8-point type; a local guarded spacing hook fails explicitly if the expected
section formatter is absent and restores that formatter on leaving the contents.

Independent QA covers all final page overviews, specified full-page details,
selected claims, all 28 person-record calculations, and 451 static local HTML
references. No current browser interaction, JavaScript, responsive/accessibility,
or offline MathJax qualification is claimed. See
`research/rendered-review-0.16.0.json` for exact hashes and scope. Historical stage02
and stage04 findings and the 64-page 0.15.0 record remain unchanged.

The final dependency lock records 34 packages and public Blake commit
`4dc75f71d28f83a9f92db9ca523fb38326ba95f6`. A separate fresh locked installation passes
620 tests, strict package typing, Ruff, dependency compatibility and byte-identical
replay of four historical analyses with 33 installed distributions. Its receipt is
`research/installation-shared-methods-0.16.0.json`. The native render retains its
original recorded environment; the new installation reverified a separate copy.
Offline workspace browser QA is blocked by the browser tool's local-file URL
policy; generated HTML and Node/Python checks do not establish browser behavior.
