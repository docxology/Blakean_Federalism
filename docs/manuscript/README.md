# Rebuild the private manuscript

Version 0.3.0 extends the article to about 7,000 words plus a selected bibliography, four original vector graphical abstracts on physical pages 1-4, and a four-plate critical atlas. The paper remains a research draft requiring specialist criticism. The original 0.1.0 concordance and 0.2.0 qualification are preserved. Version 0.3.0 adds a fresh result epoch, direct contestability scholarship and an aggregate research workbench.

Use the supported GitVault repository admission and external Python 3.11 runtime. Both Python prefixes, TMPDIR and cache bindings must resolve on the mounted volume. Install the optional renderer explicitly:

~~~bash
uv sync --locked --extra manuscript
uv run python -m tools.acquire_manuscript
uv run python -m tools.render_manuscript --output analysis_output/manuscript/new-run
~~~

The acquisition command recovers only eleven individually hash-pinned manuscript inputs: five ASU HTML texts, four official LOC JPEGs and two item metadata/rights responses. No credentials are needed. Existing valid files are retained; changed bytes, unsafe paths, symlinks and unapproved source hosts fail. A changed remote page must be reviewed and repinned in a new source epoch; do not remove checksum checks to make recovery green. A failed partial input stays inspectable. The much larger recovered corpus is a separate custody object, governed by PRIVACY.md and corpus-pin.json.

The renderer reads the article, references-and-rights.md and research/manuscript-inputs.json. It verifies all input hashes and exact selected anchor lines before creating output. The final output directory must be new and within analysis_output. An occupied directory fails without replacing earlier evidence. The PDF, generation receipt and Bitstream Vera license are written together. The receipt says visual review is pending; generation never grants its own acceptance.

Layout: US Letter, 39.6 point margins (13.97 mm), 10 point body with 12.8 point leading. Opening-page drawings are vector schematics, followed by the article on physical page 5. All four selected historical sheets appear again in a larger atlas with copy, date, credit and critical purpose. Font embedding and image scaling do not modify the captured provider inputs. Deterministic PDF metadata and content-addressed image objects support byte-identical rendering across independent input locations with pinned dependencies.

The renderer supports the current manuscript's explicit CommonMark subset: headings, paragraphs, blockquotes, emphasis, code spans and HTTPS links. Unsupported blocks, images or link schemes fail rather than disappear. Quotations are ordinary Markdown blockquotes and must match the structured ledger with exact multiplicities. The plate-52 right epigraph is separately reconstructed; the noncontiguous plate-88 excerpts declare their omission. Modern editorial locator/footnote type is excluded, spelling retained, and whitespace normalized. This is a selection verifier, not a general critical-edition parser.

For qualification:

~~~bash
uv run pytest tests -q --cov=blakean_federalism --cov=tools --cov-branch --cov-report=term-missing
uv run basedpyright
uv run ruff check src tests tools
uv run ruff format --check src tests tools
~~~

Core package typing retains ALL mode. Rendering/acquisition are separate infrastructure tools, tested with real files and real PDFs; fixed geometric coordinates and positional drawing primitives have documented lint exceptions. Application coverage must remain at least 90%; infrastructure at least 60%. Do not replace final visual inspection with text extraction. Rasterize every final page, inspect the opening four at full scale, inspect each article/reference/atlas page, and bind the resulting QA record to the PDF hash.

The project remains private. Raw source captures, scholarship downloads, selected images and generated PDFs stay ignored. Private release assets may contain this bounded PDF, software packages and source only. No public Zenodo deposit or blanket corpus-image redistribution is part of this update.

The manuscript-input version 0.2.0 identifies the preserved eleven-input selection epoch. The package and generated output version is recorded separately as 0.3.0; this update does not silently repin earlier source bytes.
