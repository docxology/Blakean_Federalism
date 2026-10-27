# Rebuild the private manuscript

Version 0.11.0 uses the actual PDF and HTML rendering infrastructure from a clean, commit-pinned checkout of [docxology/template](https://github.com/docxology/template). The pin, writer identities and citation profile are recorded in `research/template-rendering.json`. The canonical authoring files are `states-change.md`, `references-and-rights.md`, `references.bib`, `config.yaml` and `preamble.md`.

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

Layout is US Letter with 14 mm margins and 10 point body type. Four graphical abstracts occupy physical pages 1–4, followed by contents, notation and the article. Fifteen original diagrams have vector PDF masters and high-resolution PNG derivatives. Fourteen uncropped LOC sheets appear beside their readings with item-specific credits and dates. The 0.11.0 selection adds the Jerusalem frontispiece and final plate, retaining full provider images and orientation. The four graphical abstracts use original plates and italic serif quotations. Bitstream Vera and DejaVu serif licenses accompany the embedded figure fonts. Sixteen labeled formalisms, eleven labeled equations and 55 cited references use native numbering and bibliography controls. All Blake block quotations use an italic quote environment in PDF, an italic blockquote in HTML and italic verse cards in the workbench; source text remains independently checked.


Author formalisms as fenced Divs, for example `::: {.definition #def:typed title="Four typed sorts"}`, closed by `:::`. Refer to them with `[@def:typed]`. Counters are automatic within each kind. Equations use a display-math block followed by `{#eq:name}` and references `[@eq:name]`. Figures have `{#fig:name}` identifiers. Scholarly citations use `[@key, p. 17]` and an entry in `references.bib`; PDF uses natbib/BibTeX and HTML uses citeproc. The source validator rejects duplicate identifiers, unsupported or unclosed formalism blocks, unresolved references and manually numbered formalism titles. Normative axioms are explicitly proposed commitments; the propositions establish only the stated formal consequences.

The verifier checks source and figure hashes, separate output identities, the correct embedded illustration on each of physical pages 1–4, actual HTML formalism headings, bibliography identifiers, compiled PDF citation keys, and the multiplicities of 36 selected Blake quotation records (148 exact segments). It strips Markdown hard-line-break, escaped straight-apostrophe and escaped-hyphen syntax before quotation comparison. Escaping a straight apostrophe makes Pandoc emit a literal quote glyph rather than letting XeLaTeX apply a typographic substitution. The captured source spelling and punctuation remain exact. This is selection verification, not critical-edition collation. SOURCE_DATE_EPOCH and UTC are fixed, but byte-identical native rerendering is a separate empirical check rather than an assumed guarantee.

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


The front notation source is notation.md. Preparation includes its hash and places 01_notation.md after the opening abstracts/contents and before the article. Native verification requires a real notation table before the numbered argument in HTML and in physical front matter in the PDF. The table separates relation C from coverage C_q; Jac, Pr and Lift name the corpus association measures. All fifteen diagrams are regenerated from code; corpus statistics and finite intervention results retain their original analytical producers. Serialized Measure values now reject inconsistent rate/coverage denominators before a chart consumes them.
