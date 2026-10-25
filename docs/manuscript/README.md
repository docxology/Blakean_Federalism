# Rebuild the private manuscript

Version 0.4.0 uses the actual PDF and HTML rendering infrastructure from a clean, commit-pinned checkout of [docxology/template](https://github.com/docxology/template). The pin, writer identities and citation profile are recorded in `research/template-rendering.json`. The canonical authoring files are `states-change.md`, `references-and-rights.md`, `references.bib`, `config.yaml` and `preamble.md`.

The project uses its external Python 3.11 environment for preparation and verification. The pinned template uses a separately supplied compatible external Python environment. Verify both `sys.prefix` and `sys.base_prefix` for each environment, the mounted GitVault volume, external TMPDIR/cache bindings and the supported repository admission before execution. Dependencies include Pandoc, compatible pandoc-crossref, XeLaTeX, BibTeX and Poppler. Install the optional manuscript dependencies explicitly when provisioning; do not replace an active environment implicitly.

~~~bash
uv run python -m tools.acquire_manuscript
uv run blakean render-manuscript \
  --template-root "$TEMPLATE_REPO_ROOT" \
  --template-python "$TEMPLATE_PYTHON" \
  --output analysis_output/publication/new-run
~~~

The template checkout must be clean and exactly match the recorded commit. Rendering invokes `PDFRenderer.render_combined` and `WebRenderer.render_combined` after the template's manuscript injection, without a substitute body renderer. `tools/render_manuscript.py` forwards to this command; its older helper API remains for historical compatibility tests. A source checkout is needed for the native worker. The core wheel still supports the separate offline evidence workbench without the optional PDF stack.

Acquisition recovers only eleven individually hash-pinned inputs: five ASU HTML texts, four LOC JPEGs and two item metadata/rights responses. Existing valid files are retained. Changed bytes, unsafe paths, symlinks and unapproved hosts fail. A changed provider page requires a reviewed new source epoch. The larger recovered corpus is a separate local custody object under `PRIVACY.md` and `corpus-pin.json`. Modern scholarly PDFs remain local and ignored.

Preparation revalidates the copied index, every stored concordance span, the quotation selection and source hashes before creating a new stage inside `analysis_output`. Occupied outputs are refused. A completion receipt is written only after the native PDF and HTML outputs pass their content and identity checks. A failed stage and its native log remain inspectable. Rendering never grants its own visual or scholarly acceptance.

Layout is US Letter with 14 mm margins and 10 point body type. Graphical abstracts occupy physical pages 1–4, followed by the contents and article. Seven original schematic figures have vector PDF masters and high-resolution PNG derivatives. Four unchanged selected LOC sheets appear in a critical atlas with item-specific credits, dates and limits. The Bitstream Vera license accompanies the figure fonts. The manuscript-input version 0.2.0 remains the preserved selection epoch; package/output version 0.4.0 is separate.

Author formalisms as fenced Divs, for example `::: {.definition #def:typed title="Four typed sorts"}`, closed by `:::`. Refer to them with `[@def:typed]`. Counters are automatic within each kind. Equations use a display-math block followed by `{#eq:name}` and references `[@eq:name]`. Figures have `{#fig:name}` identifiers. Scholarly citations use `[@key, p. 17]` and an entry in `references.bib`; PDF uses natbib/BibTeX and HTML uses citeproc. The source validator rejects duplicate identifiers, unsupported or unclosed formalism blocks, unresolved references and manually numbered formalism titles. Normative axioms are explicitly proposed commitments; the propositions establish only the stated formal consequences.

The verifier checks source and figure hashes, separate output identities, first-four-page content, actual HTML formalism headings, bibliography identifiers, compiled PDF citation keys, and the multiplicities of thirteen selected Blake quotations. It strips only Markdown hard-line-break syntax before quotation comparison. This is selection verification, not critical-edition collation. SOURCE_DATE_EPOCH and UTC are fixed, but byte-identical native rerendering is a separate empirical check rather than an assumed guarantee.

The paper HTML uses the template's network MathJax profile. Its formulas need that CDN to typeset in a fresh browser. The research workbench remains a separate self-contained offline artifact. A rendering bundle can reproduce the bounded paper from included selected inputs; it is not full analytical reproduction or permission to redistribute the entire corpus.

Qualification uses real files, PDFs, images and subprocesses:

~~~bash
uv run pytest tests -q --cov=blakean_federalism --cov=tools --cov-branch --cov-report=term-missing
uv run basedpyright
uv run ruff check src tests tools
uv run ruff format --check src tests tools
~~~

Application coverage must remain at least 90 percent and infrastructure at least 60 percent; read both totals from the per-file report, since one combined floor cannot express two separate targets. The top-level README command enforces the application floor with its `--cov-fail-under` value. Inspect every final PDF page and the live HTML separately; text extraction alone cannot establish layout quality. Bind the QA record to the actual output hashes. The repository and release remain private; no public Zenodo deposit or blanket corpus-image redistribution is authorized.
