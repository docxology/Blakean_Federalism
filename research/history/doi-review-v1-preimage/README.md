# Blakean Federalism

Private research on **composition without capture**: poetic states, persons,
temporal national formations and coercive jurisdictions remain distinct. Several
nations can coexist without becoming one nation. A literary interpretation
supplies no automatic institutional warrant.

Start with [project status](docs/PROJECT_STATUS.md),
[agent guidance](AGENTS.md), the [article](docs/manuscript/states-change.md),
the [current private working-draft PDF](Blakean_Federalism.pdf) and
the [documentation map](docs/README.md).

## 2 November abstract and caption revision

The new native candidate has **79 pages** at
`analysis_output/publication/editorial-20261102-01`. Its abstract foregrounds
composition without capture; revised analytical captions state the question
before their operations and denominators. Source models, safeguards, timing
inputs, corpus identities and the 0.19.0 program remain unchanged. The actual
pinned template writers completed. All 79 pages and the exact desktop/mobile
HTML have independent working-draft output acceptance. Both current and dated
PDFs were copied byte-for-byte to Downloads; publication is recorded separately
with the exact hashes in [project status](docs/PROJECT_STATUS.md).
The preceding 78-page timing edition retains its own review evidence.

## Current application and evidence

Federalism **0.19.0** selects public Blake **0.7.0**, exact Git
`263d7c83abe6f1309a64af3285a683c1b7672269`, through
[pyproject.toml](pyproject.toml) and [uv.lock](uv.lock).
Blake owns corpus custody and reusable methods; this application owns political
terms, institutional models, fixed cases, scholarly readings and the manuscript.
[The shared-method boundary](docs/shared-methods.md) also distinguishes the
current SDK from historical corpus and analysis producers. Entomology is an
independent sibling, with no runtime dependency.

The new [timing atlas](docs/research/review-timing-atlas.md) evaluates **21,454
stipulated configurations and 42,908 person records** across two declared
slices. Readiness and protection geometry retain their 102 shared
configurations. Filing, expiry, response and consequence times remain explicit,
and exposure is calculated separately for each person. The two report-derived
figures and a conditional boundary lemma distinguish empty uncovered time from
effective practical protection. Material provision, reprisal safety, reviewer
control and collective reservation remain unassessed. This is neither a sample
of real institutions nor a legitimacy score.

The original fourteen procedures, twenty-eight claimant records and fifteen
safeguards remain fixed. The separate eight-procedure
[pressure study](docs/research/review-pressure-20261029.md) retains its own
inputs and interpretation. [Procedural comparison](docs/research/procedural-comparison.md)
uses person-specific residual profiles rather than one aggregate rating.

The [current runtime record](research/runtime-profile-20261102.json) preserves
the real Python 3.15 full-suite warnings, the failing resource control and the
31-test fixture repair. The final repaired canonical gate has its own receipt.
The retained full 0.19.0 normal-installed gate passed **818 tests**. Separate
statement-and-branch coverage is **97.06% application / 75.14% tools**, against
90% / 60% floors. These results qualify the tested software source; native
writers and private-main delivery have their own bindings in
[project status](docs/PROJECT_STATUS.md). The preceding corrected 78-page native edition
passes the final independent bounded PDF/content and desktop/mobile
working-draft review, including all 78 of its pages. Specialist equation accessibility,
whole-paper scientific acceptance and public release remain separate.
The [verification index](research/verification.json) and
[current-source index](research/current-source.json) identify current and retained
qualification records; they do not rename historical producers.

The retained 0.17.0 paper's 74-page native output and its 688-test production
qualification remain in [their dated record](research/paper-advancement-20261029.json).
The earlier 72-page edition likewise retains
[its qualification](research/expansion-installed-20261028.json).
A changed manuscript receives a new request/stage, actual pinned-template
execution and physical-output acceptance before replacing a delivered PDF.

## Read the argument

- [Notation](docs/manuscript/notation.md), [article](docs/manuscript/states-change.md)
  and [references/rights](docs/manuscript/references-and-rights.md).
- [Institutional design](docs/institutional-design.md), [primary passages](docs/primary-passages.md)
  and [research program](docs/research-program.md).
- [Annotated scholarship](docs/annotated-bibliography.md),
  [source and reading dossiers](docs/research/README.md) and
  [portfolio crosswalk](docs/portfolio-crosswalk.md).
- [Authoring conventions](docs/style-guide.md) and
  [actual template production](docs/manuscript/README.md).

The argument keeps textual warrant, interpretive bridge and institutional
warrant separate. Selected readings of Jerusalem 45, 55 and 73 put prevention,
compelled demonstration, remedial burden and provision under pressure; the
computer model does not decide those readings. Existing source/quotation ledgers
remain authoritative. The selected D02 `bowl`/`howl`
[collation](research/textual-collation-20261029.json) preserves both captured
witnesses and does not claim whole-copy collation.

The final canonical normal-installed gate passed **819 tests**, with **92.11% application / 69.02% tools** suite-only statement/branch coverage. Typing, lint, formatting and dependency checks pass. [Exact current qualification](research/visual-installed-20261102.json).

## Run locally

Keep source, both Python prefixes, environments, caches and temporary files on
mounted GitVault. Use the declared external Python 3.15 runtime and supported
repository admission. A clone includes project code and authored research; it
does not restore the ignored corpus or scholarly PDFs.

~~~bash
export UV_PROJECT_ENVIRONMENT=../../../../Local/environments/blakean-federalism-0.19.0-py315-20261102-01
uv sync --locked --python 3.15 --extra manuscript
uv run --locked python -c 'import pathlib,sys; print(pathlib.Path(sys.prefix).resolve()); print(pathlib.Path(sys.base_prefix).resolve())'
uv run --locked pytest -c pyproject.toml tests -q
uv run --locked basedpyright
uv run --locked ruff check src tests tools
uv run --locked ruff format --check src tests tools
~~~

Both printed prefixes must resolve on GitVault. Bind external `TMPDIR`,
outer `TMPPREFIX`, `UV_CACHE_DIR` and `UV_LINK_MODE=copy` before gates.
The project has separate application and infrastructure coverage floors; read
both denominators rather than treating a combined percentage as both gates.
The [native guide](docs/manuscript/README.md) declares optional rendering
dependencies and the separately pinned template runtime.

Produce a new timing epoch from the four source-pinned research inputs:

~~~bash
uv run --locked blakean timing-atlas --root . \
  --output analysis_output/timing-new --figures
~~~

The destination must be unused. The completion receipt binds inputs, producers,
exact analytical exports and figures. It is source/output custody, not
independent recomputation, rendered-page acceptance or empirical validation.

## Search and contextual review

The retained projection at
`local_data/corpus/blake-v0.2.0-qualified` contains 2,067 source units:
540 reading, 731 XML and 796 editorial/mixed Erdman units. Its roles remain
199 primary, 1,068 unverified and 800 editorial/mixed. These are retained
source/copy/page units, not unique Blake works. Keep the
[corpus pin](research/corpus-pin.json) and original projection intact.

~~~bash
uv run --locked blakean search-corpus --term "minute particulars" \
  --output analysis_output/particulars-new.json
uv run --locked blakean search-corpus --term state --term individual \
  --mode all --window-words 32 --output analysis_output/state-person-new.json
uv run --locked blakean build-search-workspace \
  --output analysis_output/search-workspace-new
~~~

[Search](docs/corpus-search.md) accepts literal terms and explicit role,
plane, work and word-window filters. Full text stays private and ignored.
The [evidence workbench](docs/research-workbench.md) carries aggregate
diagnostics and reading bounds. Generic search and workspace behavior belong
upstream.

[Contextual review planning](docs/research/review-planning.md) selected a blank
25-candidate workload from 223 scoped hits. Planning adds no authored decisions
or independent-observation claim. Authored labels must bind the original run,
hit, named reviewer, rationale and required locator; they do not recode
quotation records or institutional cases.

For a new capture or independent projection, declare a new pin and unused
destination and pass it explicitly to every consumer. Never reimport over the
qualified baseline. Keep zero cells, repeated witnesses, original offsets and
source-author distinctions. Retrieval completeness within declared bytes is
different from literary coverage.

## Scope and delivery

Scholarly reading, copy collation, real institutional effectiveness, accessibility
and public item-level rights remain separate acceptance questions.
[Project status](docs/PROJECT_STATUS.md) scopes their next useful units.
Prior author-index counts, reported complete-extraction readings and portfolio
observations remain dated evidence in the retained ledgers; search adds no
reading credit.

Provider bodies, images, indexes, original briefs, full concordances and
scholarly PDFs stay in authorized ignored custody. Ordinary private-main
publication and Downloads delivery require exact final source/output bindings
and fresh remote readback. They grant no public redistribution permission.
See [privacy](PRIVACY.md).
