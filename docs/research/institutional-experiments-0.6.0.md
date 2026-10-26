# Finite institutional interventions: methods, results and integration

The new API evaluates the complete powerset of twelve declared safeguard interventions against the existing fifteen predicates. It keeps the ten synthetic starting records and the assessor unchanged. The report stores every intervention's field paths and replacement values, baseline applicability, singleton effects, pair interactions, repair bundles and full-family counts. We preserve the baseline action label and manipulate the declared safeguard fields.

## Delivered API

- `institutional_experiments.run_experiment(records, available=ALL_INTERVENTIONS) -> InstitutionalExperiment`.
- `institutional_experiments.run_decision(record, available=ALL_INTERVENTIONS) -> DecisionExperiment`.
- `institutional_interventions.rule_is_triggered(record, code) -> bool`; unknown rule identifiers raise `ResearchError`.
- `institutional_interventions.apply_interventions(record, operators) -> Decision`; only failed selected predicates are edited, and protected-context equality is required.
- `institutional_interventions.verify_protected_context(before, after)` raises on changes outside the declared field domain.
- Models and `Intervention` enum are in `institutional_experiment_models.py`. `CATALOG` is public in `institutional_interventions.py`.

Canonical output is `decision-experiments.json`. `producer-receipt.json` binds its bytes and seven producer/input/test files. The report is 206,153 bytes and contains no workstation paths. Parent may copy the report into a tracked research location while preserving this producer receipt. It is a new experiment epoch; it does not replace the historical concordance producer.

## Formal definitions for manuscript numbering

**Activated obligation.** Let $q_i(d)\in\{0,1\}$ denote the stored pass result for rule $i$ in decision $d$, and $\tau_i(d)\in\{0,1\}$ its applicability. Ten rules are unconditional. Poetry-to-power and authority-gap apply when coercion is present; affected-nonmember standing applies when the affected-nonmember list is nonempty; burden allocation applies to a resource decision; treaty/refusal treatment applies when implicated. The active failure indicator is

$$f_i(d)=\tau_i(d)\,[1-q_i(d)].$$

An inactive implication's stored pass is retained for reproducibility but drawn separately from an activated, satisfied obligation. This yields three graphical states: inactive, active-satisfied, active-failed.

**Restricted field intervention.** Let $H$ be the twelve-operator catalog and $T_S(d)$ the result of selecting $S\subseteq H$. An operator changes only its declared fields and is the identity when its associated rule already passes or is inactive. Missing strings and reach are supplied only when blank; existing nonblank details survive. Let $\pi(d)$ be the complete record with the catalog's editable fields removed. Every transformation must satisfy

$$\pi(T_S(d))=\pi(d).$$

The protected projection includes subject and authority identities/types; national affiliations and poetic interpretation; classification warrant and source; action label; coercion; resource-decision status; all affected persons and nonmembers; treaty/refusal implication; and provenance. Thus intervention cannot obtain admission by deleting affected people, turning off resource duties or making coercion disappear. A separate guard rejects a changed projection.

**Minimal predicate repair.** Define the failed-rule set $F_d(S)$ and admission indicator $A_d(S)$ by

$$F_d(S)=\{i:f_i(T_S(d))=1\},\qquad A_d(S)=\mathbf{1}[F_d(S)=\varnothing].$$

The reported minimal bundles are the inclusion-minimal admitted subsets, and the minimum cardinality is

$$m(d)=\min\{|S|:S\subseteq H,\ A_d(S)=1\}.$$

An admitted baseline has the empty bundle and $m(d)=0$. A family with no admitted subset has no minimal bundle and an undefined minimum (`null` in JSON), rather than zero. Essential interventions are the intersection of all admitted subsets. Irreparable rules are the intersection of the failed-rule sets over the whole declared family. Cardinality counts catalog operations; it does not assign policy costs or rank populations.

**Complementarity of admission.** For two operators $h,k$, the report computes

$$\Delta_{hk}A_d=A_d(\{h,k\})-A_d(\{h\})-A_d(\{k\})+A_d(\varnothing).$$

A value of one identifies a pair jointly required for admission when neither alone suffices. The report separately compares the number of resolved rules against the sum of singleton resolutions. Admission complementarity can therefore coexist with completely independent rule corrections. A diagnostic fixture also tests overlapping corrections: a stipulated charter supplies both the required warrant and the missing competence source, so one operator can resolve two failures.

## Exact findings

Each record has $2^{12}=4,096$ selected subsets. Across ten records, the experiment evaluates **40,960 subsets**. Satisfied and inactive operators are identities, leaving **31 distinct transformed field states**, counted separately within each starting record. **25,600 subsets** satisfy all predicates. This fraction follows from the declared finite catalog and is not treated as a probability of political success.

The starting records contain **150 stored rule results**. **118 rules are activated: 107 satisfy their obligation and 11 fail it.** The remaining **32 are inactive**. The conditional part comprises twelve activated coercion checks across six coercive records, two affected-nonmember checks, two resource checks and two treaty/refusal checks; the ten unconditional rules supply the other one hundred activated results.

| Starting record | Minimum operations | Unique minimal bundle | Distinct states | Admitted subsets / 4,096 |
|---|---:|---|---:|---:|
| A-capture: exclusive nationality registration | 3 | Equal personhood; overlapping affiliation; supported exit | 8 | 512 |
| B-capture: co-national capture across jurisdictions | 2 | Non-exhaustion of persons; contestation | 4 | 1,024 |
| C-capture: interpretation claims police/tax competence | 1 | Separate stipulated charter | 2 | 2,048 |
| D-capture: vision-based civic rank | 2 | Remove vision rank; equal personhood | 4 | 1,024 |
| E-capture: water decision excludes affected people/costs | 3 | Affected-nonmember standing; burden allocation; treaty/refusal | 8 | 512 |
| Each of A–E bounded | 0 | Empty bundle | 1 | 4,096 |

Every starting record has one inclusion-minimal bundle. For the five capture records the catalog repairs the initial failures independently: if $k$ safeguards are necessary, exactly $2^{12-k}$ selected subsets contain them, and exactly $2^k$ distinct field states remain after no-ops collapse. The sum of distinct states is $5+8+4+2+4+8=31$. All subset additions preserve or reduce the failed-rule set. All protected projections match.

B and D each show one positive pair interaction: neither member of their two-operator bundle admits the record alone, whereas the pair does. All other pair interactions in the ten starting records are zero. Their resolved-rule excess is zero: the complementarity comes from conjunctive admission, not from inventing a new rule interaction. A and E require three operators; their admission bottleneck does not appear in a two-operator interaction alone.

The diagnostic shared-field fixture prevents generalizing “one operation per failure” into a law of the model. With both a missing competence source and an interpretive competence warrant, the charter operator alone resolves poetry-to-power and authority-gap. Its minimum is one despite two initial failures, and the charter/competence pair has resolved-rule excess minus one because both can supply the source.

## Controls and verification

The first focused run failed to collect because the requested new implementation did not yet exist; `red-stdout.txt`, `red-stderr.txt` and `red-exit.txt` preserve that result. Later qualification failures are retained in the root and `qualification-02/03` logs. Final `qualification-04` supports:

- **20 passing focused tests**, including the complete ten-record enumeration and independent four-subset numerical oracle.
- **225/227 covered statements plus branches (99.1189%)** across the three new modules; the remaining branch is the generic fallback for a nonstring/nonsequence blank-check input, not a catalog path.
- Ruff lint clean, formatter unchanged and basedpyright zero errors/warnings.
- No mocking frameworks, network dependencies, random sampling or external legal determinations.

The numerical and failure controls verify:

1. Removing the charter operator from C leaves no admitted subset and preserves `POETRY_TO_POWER` as irreparable.
2. Collapsing issuer, jurisdiction and subject types remains irreparable with all twelve operators; all 4,096 subsets fail and yield one distinct unchanged state.
3. Coercion, resource status and affected-nonmember mutations each fail the protected-context guard.
4. An already-admitted empty family returns the empty repair; a failed empty family returns no repair and an undefined minimum.
5. The full mutable-predicate fixture initially fails all twelve editable rules and passes after intervention, while retaining all triggering conditions.
6. Existing reasons are preserved when only representation limits are missing; selected inactive operators leave even missing competence fields untouched.
7. Unknown rules, duplicate operators, unknown operators, empty record sets and duplicate decision identities are rejected.
8. Repeating interventions is idempotent, reversing the caller's selection order yields the same canonical result, and immutable original records remain unchanged.

## Figure and caption proposal

Use the existing case-rule matrix with three marks: gray dash for inactive, open black for active-satisfied, red for active-failed. Pair it with a five-row, twelve-column minimal-bundle matrix. Align A–E rows across both panels; show minimum cardinality and distinct-state count at the right. A small legend should state “40,960 catalog subsets; 31 distinct field states” and separate the five already-admitted baselines from the five capture starting points.

Candidate caption: **Safeguards combine without erasing affected people.** The left panel distinguishes activated obligations from inactive implications across fifteen rules and ten synthetic records. The right panel marks the unique minimum field-intervention bundle for each capture record: three, two, one, two and three operations for A–E. The exhaustive twelve-operator family contains 40,960 subsets and 31 distinct field states. Coercion, resource duties, affected persons and nonmembers, treaty triggers, identities and interpretive content remain fixed. The five bounded records require no intervention.
