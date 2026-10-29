# Comparing residual procedural requirements

This new source epoch compares the existing fourteen procedures and twenty-eight
claimant records. It changes neither `research/cases.json` nor
`research/institutional-review-cases.json`. The shared baseline boundary runs the
existing `institutions.assess` and requires the linked decision to satisfy the
original fifteen safeguards. `audit_review` remains the sole producer of access
conditions and uncovered intervals. This comparison consumes that assessment.

## Meaning and assumptions

Each procedure has a residual profile: procedure-level separation/revision
failures, and each person's admission/remaining/preparation/deadline failures,
preparation shortfall, readiness lateness and exact uncovered intervals. A profile
requires a subset of another only if all categorical sets are subsets, all
shortfalls/lateness values are no greater, and each person's uncovered time is
contained in the other's uncovered time. Hours never transfer between people.
Equal-duration gaps at different instants need not be comparable.

Comparison requires the same baseline decision, claimant IDs, memberships,
required preparation hours and consequence times. Input hours share a stipulated
notice origin. The parser rejects empty procedures, invalid events and ambiguous
identities. The comparison rejects mismatched duties. It matches people by ID,
independently of input order.

This is a partial order on residual profiles, and a preorder on source procedures
until procedures with equal profiles are identified. The frontier contains all
procedures whose profile has no strictly smaller profile in this supplied family.
It is neither a scalar ranking nor a policy cost minimization. The fixed family
has empty profiles, so its frontier is the empty-profile class. Nonempty residual
sets still matter: the complete pair table and explicit requirement display show
their tradeoffs rather than discarding them after frontier selection.

An unmet requirement set identifies conditions that must cease to fail under the
stipulated target. It does not enumerate independent interventions. Fixing a
filing barrier can activate filing-triggered protection and thereby remove a
timing gap; changing a response time can also remove it. A fresh assessment is
required after any proposed change. No implementation effect is inferred here.
Raw windows, response and protection records remain in `review-report.json`, in
the new comparison's complete audit data, and in the per-person CSV. Suspension
is reported separately. H12's retaliation and disputed forum competence remain
unassessed, including when its profile is empty or equivalent to another.

## Use the existing orchestrator

```bash
uv run blakean compare-review \
  --cases research/institutional-review-cases.json \
  --decisions research/cases.json \
  --output analysis_output/review-comparison/new-epoch \
  --figures
```

In the source stage use root's explicit external environment and
`PYTHONPATH=PACKET/core:PACKET/federalism/src`. Do not install dependencies or
mistake source qualification for installed-package qualification.

The command writes a new directory with:

- `review-report.json`: the existing audit's unchanged serialization contract.
- `comparison.json`: round-trip-safe comparison data with complete audit inputs,
  person-specific residual profiles, every unordered pair and the frontier IDs.
- `claimant-requirements.csv`: all twenty-eight people with raw event/window
  values, active protection, exact gaps, deficiencies and separate forum powers.
- `procedure-comparisons.csv`: every unordered pair and its relation.
- `comparison-receipt.json`: input hashes, existing baseline assessment, the
  actual analytical producer closure and every output's hash and size.

The optional figures add deterministic vector PDF masters and 2400-pixel PNG
derivatives for `review-requirements` and `review-comparability`. They use the
packaged Vera font, ReportLab and the actual `pdftoppm` executable. Only the
fixed fourteen-by-two publication layout is supported; smaller valid studies
remain usable without figures. JSON/CSV operation imports no optional figure
stack. The receipt binds figure code/font bytes when used. Native executable and
package versions belong in the execution receipt; source hashes alone do not
identify the environment.

Validation precedes directory reservation. Occupied output, symlink output,
invalid inputs, failing baseline, changed input bytes and unsupported figures
fail explicitly. Shared Blake exclusive writers publish JSON/CSV and completion
receipts. A failed generator leaves an inspectable partial run without a
completion receipt. The final receipt is written last. Use a new epoch for any
retry. Do not erase failed runs or update historical reports.

## Publication and evidence limits

`prepare_publication` retains a complete `review-comparison` subrun, copies the
four figure files into the native figure directory and derives captions from
that same comparison. The main manuscript introduces the order's assumptions,
exact interval semantics, empty-profile equivalence and the difference between
requirements and repair actions. `research/procedural-comparison-reading-20261028.json`
records the selected primary-source reread and its ceilings.

No new empirical case, court holding, present-day legal claim, full-work reading,
quotation, corpus/search/stats/queue engine or generic graph framework is added.
The previous 69-page PDF QA remains historical. This stage prepares sources and
figures; final native PDF/HTML rendering, page inspection, installed SDK replay
and final acceptance belong to root. The existing browser file-URL hold remains.
