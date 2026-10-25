# Blakean Federalism

Private research on **composition without capture**: a federation contains STATES in the proposed Blakean sense, while NATIONS are temporal generations, combinations and productions. Several nations can coexist without becoming one nation. Poetic states, persons, national formations and coercive jurisdictions remain distinct.

This project integrates the supplied research scope and related-reading addendum, the recovered local Blake corpus, and a new primary-source research pass. It develops an article, a corpus workbench and an executable institutional comparison.

## Manuscript and workbench 0.5.0

Expanded close reading, fifteen verified Blake quotations, deeper scholarly disagreements and political comparators, four dense opening graphical abstracts in black, white and red, five body diagrams, and six item-specific LOC plates in the main text. [Rebuild and layout instructions](docs/manuscript/README.md) explain local acquisition, rights, source verification and final PDF inspection. The article remains a private research draft. The current route invokes the pinned `docxology/template` PDF and HTML renderers, with nine automatically numbered formalisms, five labeled equations and a shared citation database.

The portable, offline research workbench reconciles 180 query/plane/role cells with source-unit denominators, displays all 150 checks across ten synthetic alternatives, and exposes quotation and reading provenance. [Workbench method and use](docs/research-workbench.md). The scholarship adds complete articles by Henderson, Simpson, Mellor, Ostriker and Shachar to the retained Pettit and bounded Clark readings; The new pass adds Viscomi, Heppner, Kaplan, Fraser and Tully on production, gendered agency, counterpublics and recognition procedures; Wright's continuous chapter remains unavailable.

## Start reading

- [States Change article draft](docs/manuscript/states-change.md)
- [Institutional design and five Xeno-California case pairs](docs/institutional-design.md)
- [Primary-source research and objections](docs/research/primary-source-research.md)
- [Integration crosswalk](docs/scope-integration.md)
- [Primary passage program](docs/primary-passages.md) and [structured ledger](research/primary-passage-ledger.json)
- [Annotated scholarship and political bibliography](docs/annotated-bibliography.md)
- [Portfolio versions, reading status and correction docket](docs/portfolio-crosswalk.md)
- [Research program and acceptance criteria](docs/research-program.md)
- [Corpus observations](docs/corpus-observations.md)
- [Privacy and local recovery](PRIVACY.md)

The classification-decision record is this project's interpretive extension from Entomological Law, not an existing schema in that paper. Rahman's broader-culture/conformity proposal remains attributed to Rahman and speculative. No larger-scale-equals-freer inference, civic vision hierarchy, four-organ constitution or political square-root-of-two law is encoded.

## Run locally

Keep source, environments, caches and temporary files on GitVault. Use the existing external Python 3.11 runtime. After verifying the mounted volume and acquiring the supported repository lease:

~~~bash
uv sync --locked --python 3.11 --extra manuscript
uv run pytest tests -q --cov=blakean_federalism --cov-branch --cov-fail-under=90
uv run basedpyright
uv run ruff check src tests tools
uv run ruff format --check src tests tools
~~~

Import an independent text projection from the existing Blake project. The source is read-only, and a destination must be new:

~~~bash
uv run blakean import-corpus \
  --source ../../Public/blake/blake_data \
  --destination local_data/corpus/blake-v0.2.0
uv run blakean analyze \
  --corpus local_data/corpus/blake-v0.2.0 \
  --output analysis_output/concordance-new-run.json
uv run blakean export-summary \
  --concordance-file analysis_output/concordance-new-run.json \
  --output analysis_output/aggregate-new-run.csv
uv run blakean assess-cases \
  --output analysis_output/cases-new-run.json
~~~

Set external TMPDIR, UV_CACHE_DIR and UV_LINK_MODE=copy as described in the GitVault contract. Verify both sys.prefix and sys.base_prefix resolve on GitVault. Global Python selection alone does not establish that. A fresh machine must provision the compatible external runtime before syncing.

The project pins Blake commit d54aae1809066dd8a835ac68d4d55c61f8642d61, the capture manifest, producer projection manifest and index hashes in [corpus-pin.json](research/corpus-pin.json). It does not download or redistribute provider texts automatically. A changed upstream epoch requires an explicit new pin and a new import directory. An occupied output is refused, preserving prior evidence.

The imported projection has 2,067 source units: 540 reading documents, 731 XML units and 796 retained Erdman pages. Roles remain 199 primary, 1,068 unverified and 800 editorial/mixed. These are not unique Blake works. The larger source/image capture remains in the Blake project; this import does not duplicate it or close its 28 unresolved image identifiers.

## Evidence and scope

The October 23 author-index snapshot used here reports 226 works and 205 scanned texts, with 21 included Blake-related entries. The scope's 223/202 and addendum's 224/203 snapshots remain dated history. All 21 current extraction hashes were matched; that is retrieval identity, not 21 new complete reads.

[reading-ledger.csv](research/reading-ledger.csv) preserves nine reported core complete-extraction reads, three reported related complete short-work reads and nine related selected-context reads. Current-session selected readings and their limits are documented separately. Every cited edition, image, video and secondary authority has not been audited.

The ten synthetic case alternatives test explicit safeguards. A passing assessment is not legal authorization or political legitimacy. Larger social scale and three/four/six interpretive lenses cannot manufacture a freedom score. Category-theoretic and active-inference extensions remain later research options.

Original DOCX files, normalized full scope extractions, downloaded papers, full concordances and imported indexes are local and gitignored. Git cloning recovers code, project-authored research, ledgers and aggregate results; it does not recover restricted source bodies. See [PRIVACY.md](PRIVACY.md).

## Analysis and software epochs

The original full concordance and research/analysis-run.json are preserved with their producing core source in the initial Git commit. A later import-publication correction uses exclusive destination creation, exclusive file copies and a completion marker written last. Current qualification and the source-bound analytical epochs are recorded separately in research/current-source.json and research/verification.json. The original receipt is preserved. A fresh 0.3.0 full concordance is compared with that historical run and bound separately; equality of results does not retroactively change the earlier producer. CSV byte identities are preserved explicitly by .gitattributes.
