# Auditing individual access to institutional review

This Federalism-specific extension keeps the existing decision `E-bounded` fixed and supplies fourteen hypothetical review procedures for two listed individuals. It separates a named forum from the conditions under which a person can bring a challenge and remain protected while awaiting a response. It adds no corpus matcher, importer, source model, generic artifact ledger or shared search workspace.

## Inputs and event conventions

`research/institutional-review-cases.json` binds the exact bytes of `research/cases.json` by SHA-256. The command verifies that binding, parses the linked decisions and checks that their existing safeguards pass. Each new procedure names its issuing office, reviewing office, admitted individuals and powers. Each individual has membership status, an exit requirement, preparation capacity, filing readiness, a consequence time and optional interim protection. All clock values are exact integer event hours measured from notice at hour zero.

Preparation capacity comprises usable, nonoverlapping hours within the filing window. Support-enabled hours describe time made usable by stipulated assistance; they are not money, staff time or a measured treatment effect. Readiness means that submission prerequisites have been completed, rather than the time preparation begins. The earliest possible filing is the later of window opening and readiness. Filing at the closing instant is permitted. A response at the consequence instant acts first under the declared event order.

Protection occupies the half-open interval `[start, end)`. A protection ending exactly at the response covers the waiting interval. Automatic protection starts independently of filing. Filing-triggered protection starts no earlier than a feasible filing; admission, remaining affiliated, enough preparation hours and readiness by closing must all hold. Protection that has already expired cannot activate on filing.

## Seven separate conditions

For each listed individual the evaluator checks:

1. The procedure admits that individual.
2. The individual can contest while remaining affiliated.
3. Available plus support-enabled preparation hours meet the individual's requirement.
4. The individual can file by the inclusive deadline.
5. The response precedes the consequence, or protection covers the entire intervening wait.

At procedure level it also checks distinct issuing/reviewing office identifiers and power to revise the act. Suspension power is reported separately. Different office identifiers establish issuer separation; appointments, budget control and practical independence require further institutional information. The report keeps every condition and each individual's uncovered intervals. It assigns no aggregate score.

The conjunction concerns every **listed individual**. Listing two people does not establish that all affected people were identified. Individual standing also does not settle collective or treaty competence. H12 explicitly retains retaliation and disputed forum competence while satisfying all seven declared conditions.

## Fixed comparisons

| Procedure | Changed premise | Result to inspect |
|---|---|---|
| H01 | Response at 10 h, before consequences at 12/18 h | All seven declared conditions hold |
| H02 | Nonmember has 3 h against 4 h required | Individual hours fail despite 9 h aggregate capacity |
| H03 | Nonmember ready at 9 h; deadline 8 h | Filing readiness fails |
| H04 | Response at 20 h; no protection | Nonmember uncovered 8 h; member uncovered 2 h |
| H05 | Automatic protection `[12,20)` | Both waiting intervals covered |
| H06 | Nonmember protection starts at 13 h | Initial 1 h gap |
| H07 | Nonmember protection ends at 19 h | Final 1 h gap |
| H08 | Nonmember not admitted | Standing fails |
| H09 | Nonmember must leave affiliation | Remaining while contesting fails |
| H10 | Issuing office also reviews | Office separation fails; revision power remains |
| H11 | Forum can suspend but cannot revise | Revision condition fails |
| H12 | All conditions; retaliation and competence unassessed | Shows what the conjunction leaves open |
| H13 | Filing opens 14 h; automatic protection starts 12 h | Pre-filing protection covers the wait |
| H14 | Same window; protection begins only on filing | Nonmember uncovered from 12 to 14 h |

These are constructed comparisons, not a sample of actual institutions. Their purpose is to show which procedural details are underdetermined by the original decision record. They leave the existing fifteen safeguards and finite intervention family unchanged.

## Running and interpreting the output

```bash
uv run python tools/audit_institutional_review.py \
  --cases research/institutional-review-cases.json \
  --decisions research/cases.json \
  --output analysis_output/institutional-review/run-01 \
  --figures
```

Use the project environment and manuscript extras for figures; vector masters are rasterized with the actual `pdftoppm` executable. The output must be a new directory. Invalid study data, source-hash mismatches, missing or failing baseline decisions, and occupied outputs fail explicitly. The report contains the complete declared study, individual intervals and calculated conditions. The receipt binds source inputs, baseline assessments and output hashes. Figures are generated from this report: a condition matrix for all fourteen procedures and a shared-hour timeline for seven selected nonmember traces.

Tests exercise interval endpoints, individual capacity, deadlines, excluded and forced-exit claimants, advice versus revision, automatic versus filing-triggered protection, malformed inputs, expired protection and real subprocess output preservation. The manuscript supplement supplies the argument and sources; the calculation states exactly which stipulated premises it evaluates.
