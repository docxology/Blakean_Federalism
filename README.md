# Blakean Federalism

Research on **composition without capture**: poetic states, persons,
temporal national formations and coercive jurisdictions remain distinct. Several
nations can coexist without becoming one nation. A literary interpretation
supplies no automatic institutional warrant.

Start with [project status](docs/PROJECT_STATUS.md),
[agent guidance](AGENTS.md), the [article](docs/manuscript/states-change.md),
the [published 1.0.0 working-paper PDF](Blakean_Federalism.pdf) and
the [documentation map](docs/README.md).
[Maintenance and retained evidence](docs/maintenance.md) distinguish current
instructions from immutable release sources and protected worktrees.

## Public 1.0.0 edition

Federalism **1.0.0** selects public Blake **0.7.0**, exact Git
`263d7c83abe6f1309a64af3285a683c1b7672269`, through
[pyproject.toml](pyproject.toml) and [uv.lock](uv.lock). Blake owns corpus
custody and reusable methods. Federalism owns political terms, institutional
rules, stipulated cases, scholarly readings and the manuscript. Entomology is
an independent sibling, with no runtime dependency.
[Shared-method boundary](docs/shared-methods.md).

The published 76-page *States Change* edition uses the actual pinned template writers,
11 mm margins, 4 mm footer spacing and unchanged 10-point body type. Four opening
graphics lead to contents on page 5. The scene cards now join exact Blake
quotations, selected scholarship and institutional questions; the repair graphic
shows selection, application, all fifteen safeguards and recording; the corpus
graphic adds leave-one-family ranges on a common frequency scale. These are
declared comparisons and hypothetical cases, not empirical probabilities.

The author-approved 1.0.0 edition is published at [Zenodo](https://doi.org/10.5281/zenodo.23900617) and [GitHub v1.0.0](https://github.com/docxology/Blakean_Federalism/releases/tag/v1.0.0). [Publication facts](publication.json) bind the exact approved PDF; [distribution terms](LICENSE-PAPER.md) preserve authored and third-party rights. Publication does not establish specialist scientific acceptance.

The [timing atlas](docs/research/review-timing-atlas.md) retains **21,454
stipulated configurations and 42,908 person records** in two declared slices.
The fourteen original review procedures, twenty-eight claimant records,
fifteen safeguards, pressure cases and person-specific comparisons keep their
inputs and interpretation. Empty uncovered time establishes no practical or
political legitimacy. [Procedural comparison](docs/research/procedural-comparison.md).

Fresh 1.0.0 workbench execution preserves every count, denominator, case,
quotation, image and reading. Four HHI values differ by one floating-point unit
between the retained Python 3.11 and new 3.15 producers; exact rational oracles
and the unaltered old/new reports are retained. No exact byte-replay claim is
made for those reports. The audit verifier now refuses a forged producer-version
sidecar while preserving the historical institutional-audit report and receipt.

The published 1.0.0 Python 3.15.1 installation passed **821 tests**,
with ResourceWarning and unraisable warnings treated as errors, strict typing,
Ruff and formatting. Separate suite-only statement/branch coverage is
**92.17% application / 69.02% tools**; all 106 application and
163 exact SDK runtime/resource members match. See the [published-edition qualification](research/review-candidate-1.0.0.json),
[project status](docs/PROJECT_STATUS.md) and [render guide](docs/manuscript/README.md)
for distinct native, independent review, canonical consumer and delivery claims.
The 79-page editorial edition and preceding timing/pressure papers retain
their original producers and acceptance evidence.

Read the [article](docs/manuscript/states-change.md), [notation](docs/manuscript/notation.md),
[references and rights](docs/manuscript/references-and-rights.md),
[research dossiers](docs/research/README.md), [annotated bibliography](docs/annotated-bibliography.md)
and [authoring conventions](docs/style-guide.md). Textual warrant,
interpretive bridge and institutional warrant remain separate. The selected
D02 `bowl`/`howl` [collation](research/textual-collation-20261029.json) preserves
both captured witnesses and does not claim whole-copy collation.

## Run locally

Keep source, both Python prefixes, environments, caches and temporary files on
mounted GitVault. Use the declared external Python 3.15 runtime and supported
repository admission. A clone includes project code and authored research; it
does not restore the ignored corpus or scholarly PDFs.

~~~bash
uv sync --locked --no-editable --extra manuscript
uv run --locked --no-sync python -c 'import pathlib,sys; print(pathlib.Path(sys.prefix).resolve()); print(pathlib.Path(sys.base_prefix).resolve())'
uv run --locked --no-sync blakean --help
uv run --locked --no-sync pytest -c pyproject.toml tests/test_publication_source_closure.py -q
~~~

Both printed prefixes must resolve on GitVault. Bind external `TMPDIR`,
outer `TMPPREFIX`, `UV_CACHE_DIR` and `UV_LINK_MODE=copy` before gates.
The project has separate application and infrastructure coverage floors; read
both denominators rather than treating a combined percentage as both gates.
The [native guide](docs/manuscript/README.md) declares optional rendering
dependencies and the separately pinned template runtime.

The commands above are the bounded source-only profile. See
[public reproduction](docs/public-reproduction.md) for its scope. Restore only
the exact authorized fixtures before the full suite; missing-fixture errors
are not a pass.

## Verification

Post-release maintenance removes the unused statistics re-export and bootstrap
renderer. The active installed CLI and shared statistics remain in use;
[the new qualification](research/methods-retirement-20261103.json) records the
current source and separate coverage denominators. The 821-test published
qualification above remains attached to its original source.

~~~bash
: "${COVERAGE_FILE:?Select an unused external coverage database}"
export COVERAGE_FILE
BLAKE_APP_PACKAGE_DIR="$(uv run --locked --no-sync python -c 'from pathlib import Path; import blakean_federalism; print(Path(blakean_federalism.__file__).resolve().parent)')"
uv run --locked --no-sync pytest -c pyproject.toml tests -q \
  --cov=blakean_federalism --cov=tools --cov-branch --cov-report=term-missing
uv run --locked --no-sync coverage report --data-file "$COVERAGE_FILE" \
  --include "$BLAKE_APP_PACKAGE_DIR/*" --fail-under 90
uv run --locked --no-sync coverage report --data-file "$COVERAGE_FILE" \
  --include "$PWD/tools/*" --fail-under 60
uv run --locked --no-sync basedpyright
uv run --locked --no-sync ruff check src tests tools
uv run --locked --no-sync ruff format --check src tests tools
~~~

The application report includes the exact normally installed package; the tool
report includes this checkout's complete tools directory. Retain the full raw
database, including deliberately changed source-overlay fixtures, but do not
merge their counters into the unchanged product's denominator. No excluded
product modules or lower floors are introduced. Post-install commands use
--no-sync to preserve the qualified normal environment.

These full gates require retained research fixtures. New native output also
requires the [pinned template workflow](docs/manuscript/README.md) and
independent complete-page/browser acceptance.

## Timing analysis

Produce a new timing epoch from the four source-pinned research inputs:

~~~bash
uv run --locked --no-sync blakean timing-atlas --root . \
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
uv run --locked --no-sync blakean search-corpus --term "minute particulars" \
  --output analysis_output/particulars-new.json
uv run --locked --no-sync blakean search-corpus --term state --term individual \
  --mode all --window-words 32 --output analysis_output/state-person-new.json
uv run --locked --no-sync blakean build-search-workspace \
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
scholarly PDFs stay in authorized ignored custody. Ordinary main
publication and Downloads delivery require exact final source/output bindings
and fresh remote readback. Public distribution covers the selected approved payload; it does not relicense restricted inputs.
See [privacy](PRIVACY.md).

## Related projects and editions

| Project | GitHub | Zenodo |
|---|---|---|
| Corpus and shared methods | [blake](https://github.com/docxology/blake) | [Paper 0.5.0](https://doi.org/10.5281/zenodo.23921364) |
| Invertebrate readings and concordance | [Blakean Entomology](https://github.com/docxology/Blakean_Entomology) | [1.0.0](https://doi.org/10.5281/zenodo.23900583) |
| Political argument and institutional models | [Blakean Federalism](https://github.com/docxology/Blakean_Federalism) | [1.0.0](https://doi.org/10.5281/zenodo.23900617) |

[Publication and reproduction verification](docs/public-reproduction.md) records the completed publication and separates
immutable release inputs from later documentation and remaining research.

[GitHub, citation and dependency maintenance](docs/github.md) records hosted settings, checks and the current-versus-archive update policy.
