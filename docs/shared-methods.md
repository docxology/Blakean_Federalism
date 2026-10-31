# Shared methods and authored evidence review

The 0.18 application delegates corpus custody, passage schemas, regex
concordance, literal search, word-window proximity, statistics and offline search
rendering to `blake.methods`. This repository owns the political query registry,
fixed comparison grid, institutional models, readings and manuscript. Its
institutional conclusions are not corpus metadata.

## Current software and historical evidence

The current integration selects public Blake 0.5.0 at
`36b874e76d7e0549d0ea6b9f0713ced7fb41afa8`. The exact executable dependency is
declared in [pyproject.toml](../pyproject.toml) and [uv.lock](../uv.lock), with
its measured qualification in [verification.json](../research/verification.json).
The moving upstream `main` is the development source, not an implicit repin of
a completed application run. The core's
[working paper](https://doi.org/10.5281/zenodo.23770249) documents shared
infrastructure rather than the Federalism argument.

| Shared core responsibility | Federalism responsibility |
|---|---|
| Source custody, portable schemas and source identities | Select the private study snapshot and retain its historical corpus pin |
| Distinct regex, literal and normalized retrieval contracts | Supply political terms, contexts, query profiles and interpretation ceilings |
| Generic statistics, proximity, annotation custody and workspace mechanics | Define the study grouping and authored reading labels; inspect counterreadings |
| Source-bound outputs and exclusive artifact publication | Define the fifteen safeguards, person-specific review premises and residual-profile comparison |

The fourth row's institutional requirements remain domain code here; shared
custody of annotation files is different from institutional access to review.

The [dated pressure extension](research/review-pressure-20261029.md) adds eight
H12-derived procedures while retaining those original fourteen procedures and
fifteen safeguards. It keeps calculated access conditions separate from declared
practical premises, with no combined legitimacy score. Its domain adapter reuses
the existing institutional review evaluator; generic producer and output custody
remain in the public package.
See [project status](PROJECT_STATUS.md) for current task ownership and acceptance.

The [28 October installed 0.16.0 migration qualification](../research/installation-shared-methods-0.16.0.json) records the four-file byte-identical replay on the independently copied 2,067-unit input: concordance, descriptive statistics, literal study and proximity. Its selected public Git source was `4dc75f71d28f83a9f92db9ca523fb38326ba95f6`. Those producer receipts include the delegated shared source files. The current [0.18.0 planning qualification](../research/review-planning-20261030.json) has its own installed suite and blank-batch controls; it does not claim a new mathematical replay.
Historical producer identities, corpus pins and acceptance packets remain
historical; numerical equality does not replace them with a new producer.
The earlier 72-page paper used SDK `d020f47767996a061b6f60e93a82da9386a7926c`.
The retained 74-page 0.17.0 paper used SDK
`45171a099a6a658c52ab689501de646a28485653`;
the corpus capture records its earlier producer separately. Qualifying the
current SDK preserves both records and writes a new execution receipt.

## Plan a bounded contextual workload

The [request-pinned planner](research/review-planning.md) reuses public
Blake's ranking, unit caps and immutable blank batches. Federalism supplies
the original candidate run, political scope and decision labels. This is
contextual evidence review, separate from the institutional review model.
No quotation or reading ledger is converted into a candidate decision.

## Prepare a private review queue

```bash
uv run blakean prepare-evidence-review \
  --corpus local_data/corpus/blake-v0.2.0-qualified \
  --pin research/corpus-pin.json \
  --queries research/queries.json \
  --output analysis_output/evidence-candidates-001
```

Retain the SHA-256 of the completed `run.json` outside that directory. The run
binds the queries, corpus pin, complete source-bound hits, summary and blank CSV
queue. Copy the queue before adding decisions. Keep all ten evidence columns and
the fourteen-column header unchanged. Blank decisions remain unreviewed.

The private labels are `textual_support`, `counterreading`, `nonpolitical` and
`uncertain`. Each decision requires a named reviewer and rationale. Support and
counterreading also require a verification locator. A label records an authored
reading; it does not change source authorship or confer institutional authority.

```bash
uv run blakean review-evidence \
  --run analysis_output/evidence-candidates-001 \
  --run-sha256 SHA256_RETAINED_FROM_THE_COMPLETED_RUN \
  --decisions analysis_output/authored-reading.csv \
  --output analysis_output/evidence-review-001
```

CSV and JSONL are supported. Review retains the authored bytes, normalized
decisions and a completion receipt. Counts distinguish identified Blake-primary
reading hits from exploratory source material. Omitted candidates are never
automatically classified as nonpolitical. A later producer can review a pinned
historical queue; the result records the candidate producer and review producer
separately.

Loaders parse the exact receipt and payload bytes they verified, so replacing a
pathname after verification cannot substitute a different corpus or candidate
set. Publications use the shared exclusive writer anchored to a verified
directory descriptor. These are custody controls, separate from the literary
merits of a reading and from the standing, time and remedial powers needed for
institutional review.

Full contexts, queues and local offline workspaces stay under ignored
`analysis_output/`. Use a new directory for each run and preserve failed partial
runs. A clone contains source code and project-authored research, not the private
corpus. The software dependency pin and historical corpus pin identify different
objects.
