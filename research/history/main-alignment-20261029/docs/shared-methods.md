# Shared methods and authored evidence review

The 0.16 software candidate delegates corpus custody, passage schemas, regex
concordance, literal search, word-window proximity, statistics and offline search
rendering to `blake.methods`. This repository owns the political query registry,
fixed comparison grid, institutional models, readings and manuscript. Its
institutional conclusions are not corpus metadata.

The migration retains the historical regex and literal contracts. A fresh run on
the independently copied 2,067-unit input reproduces all four historical JSON
measurements byte for byte: concordance, descriptive statistics, literal study and
proximity. New producer receipts include the delegated shared source files.
Historical producer identities, corpus pins and acceptance packets remain
historical; numerical equality does not replace them with a new producer.

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
