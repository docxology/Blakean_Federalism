# Blakean Federalism

Private research on **composition without capture**: a federation contains STATES in the proposed Blakean sense, while NATIONS are temporal generations, combinations and productions. Several nations can coexist without becoming one nation. Poetic states, persons, national formations and coercive jurisdictions remain distinct.

This project integrates the supplied research scope and related-reading addendum, the recovered local Blake corpus, and a new primary-source research pass. It develops an article, a corpus workbench and an executable institutional comparison.

## Federated inference, denser comparisons and close reading 0.12.0

The four opening figures combine original Blake plates, serif epigraphs, explicit relations and source-bound evidence. The argument distinguishes persons, poetic states, national formations and institutions. All 22 notation entries were independently checked against definitions and implementation.

The opening puts Los's system-making beside the individuals he strives to deliver from systems. New readings of Stefanis and Stephen Clark develop artistic selection, competing interpretations of creation and the authority to revise a common form. A longer single-paragraph abstract joins the literary, institutional and computational argument. Thirty-six source-verified quotation records and fourteen identified LOC sheets accompany the readings; Blake quotation blocks are italic in the native paper and evidence workbench.

The [front notation table](docs/manuscript/notation.md) distinguishes poetic sorts, institutional claims, safeguard operations and measured text. It defines complete word windows and participating matches, preserves the family identity of deletion rates, and separates query indices from assigned roles and institutional indices. Sixteen formalisms and eleven equations use the pinned docxology/template route; 57 cited references have structured bibliography records.

Sixteen original diagrams connect the argument and its recorded comparisons. The revised figures show exact occurrences, unit/family coverage, source weighting, conditional directions, all 150 safeguard checks and complete intervention-size profiles. A new two-lane comparison joins the federated-inference sources to the institutional questions of standing, warrant and review. The theme is black, white and red, with red hyperlinks. [Opening research](docs/research/opening-scholarship-0.10.0.md); [rendering instructions](docs/manuscript/README.md).

The 0.7.0 [Urizen context audit](docs/research/urizen-context-0.7.0.md) identifies all 49 state matches as seven repeated refrains in seven retained inputs. The statistical analysis retains 199 primary extracts, 644,245 word tokens and 33 recorded source-family groups. It compares pooled and equal-family rates, exact-text deduplication, 660 family omissions and 570 pair associations. The institutional experiment enumerates twelve declared interventions over ten baselines: 40,960 subsets, 31 distinct resulting records, protected material context and explicit minimum bundles. [Corpus methods](docs/research/corpus-statistics-0.6.0.md) and [finite interventions](docs/research/institutional-experiments-0.6.0.md).

The offline workbench reconciles all 180 query/plane/role cells and 150 baseline checks, separates active satisfied/failed rules from inactive conditions, and exposes the new analytical summaries, minimum bundles and complete text-free analytical data. The 0.8.0 scholarship reads Moyer’s complete article and Mitchell’s complete seminar paper, adds a Last Judgment countertext on visionary nations and follows textile work through hunger, delight and dependence. [New readings](docs/research/corpus-search-scholarship-0.8.0.md); [prior readings](docs/research/scholarship-density-0.7.0.md). [Workbench use](docs/research-workbench.md).

## Search the whole imported corpus

The [local search workspace](docs/corpus-search.md) searches arbitrary words and phrases across 2,067 imported source units, with primary text selected by default. Choose alternatives, require all terms in one source unit, or add a 1–200-word envelope for nearby combinations; filter source roles/planes/families, inspect exact highlighted spans and open source records. Family distributions and the source-layer matrix retain all counts before pagination. The full-text workspace remains local and ignored; the distributable evidence workbench contains aggregates.

~~~bash
uv run blakean search-corpus --term "minute particulars" --output analysis_output/particulars.json
uv run blakean search-corpus --term state --term individual --mode all --limit 200 --output analysis_output/state-person.json
uv run blakean search-corpus --term state --term individual --mode all --window-words 32 --output analysis_output/state-person-near.json
uv run blakean build-search-workspace --output analysis_output/corpus-search/new-run
uv run blakean search-study --output analysis_output/literal-study.json
~~~

Open the generated index.html directly in a browser. No server or runtime network is required.

## Start reading

- [Notation and reading conventions](docs/manuscript/notation.md)
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

The classification-decision record extends the role distinctions in Entomological Law. Rahman motivates the comparison between agreement through translation and agreement through dependency. The executable safeguards keep civic standing independent of official vision rankings and interpretive labels.

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
uv run blakean corpus-statistics \
  --corpus local_data/corpus/blake-v0.2.0 \
  --output analysis_output/statistics-new-run.json
uv run blakean experiment-cases \
  --output analysis_output/interventions-new-run.json
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
