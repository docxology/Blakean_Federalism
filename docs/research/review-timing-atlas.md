# Timing, protection and the power to contest the clock

This study evaluates two declared slices of a stipulated review procedure.
Its cells are parameter configurations, not additional institutions, literary
readings, observations or a probability distribution. The original H01–H14
and P01–P08 inputs and their historical outputs remain unchanged.

Public Blake supplies half-open interval difference. Federalism supplies
the people, duties, filing conditions, protection trigger, grid, practical
premises, interpretation and drawings. Generic set geometry does not decide
whether a person can file or whether an office has a warrant.

## Inputs and counting units

[The schema-1 specification](../../research/review-timing-atlas-v1.json) pins
the exact H-study, pressure study and baseline decision bytes. The loader also
checks their internal cross-links and requires the declared H12 roster,
capacities and duties. P04/P07/P08 retain the source of the earlier resident
consequence. Individually updated hashes do not excuse a contradictory anchor.

The reference is E-bounded, with water-board as issuer, review-panel as reviewer,
revision power, a filing window from 2 h through 8 h inclusively, and both
member-a and resident-b admitted without affiliation exit. Member-a has 6
available, 0 support-enabled and 4 required preparation hours, completed
readiness at 4 h, and consequence at 18 h. Resident-b has 1 available, 3
support-enabled and 4 required hours. Readiness means completed prerequisites;
it is not inferred from the nominal preparation capacity.

Two duties remain separate: resident consequence at 12 h (*original-duty*)
or 3 h (*early-threat*). The separately named treaty-people are not substituted
for the individual resident. All four practical relations remain **unassessed**:
material provision, reprisal safety, reviewer control and collective reservation.
H12's original retaliation and disputed-competence issues remain visible too.

| Declared slice | Parameters | Memberships |
|---|---|---:|
| Readiness | 2 duties × 17 response times (8–24 h) × 11 resident readiness times (0–10 h) × 3 activation modes | 1,122 |
| Protection geometry | 2 duties × 17 response times × 2 protected modes × 300 strict bands with integer endpoints 0–24 h, plus one absent-band cell per duty/response | 20,434 |

Readiness cells use the band from the resident consequence to 20 h when a
protected mode is selected. Geometry cells fix resident readiness at 6 h.
The slices share 102 logical cells, so the union contains 21,454 configurations
and 42,908 named person records. Slice memberships are retained; shared cells
are evaluated once. This is exhaustive within these two slices, not a complete
joint enumeration of every clock parameter.

Each protected cell declares the same band and supply-guarantor provider for
both people. Activation is still calculated separately. This is an explicit
new two-person extension, not a claim that the historical H/P anchors already
protected both people. The filing window and each person's capacity remain
fixed; no aggregate capacity or averaged exposure is substituted.

## Formal scope

For person \(i\), let \(o,c\) be opening/closing, \(a_i\) completed readiness,
\(q_i\) consequence, and \(r\) response. Earliest filing is
\(f_i=\max(o,a_i)\). Filing feasibility \(A_i\) requires admission, remaining
affiliated, sufficient usable preparation hours, and \(f_i\leq c\).

An automatic declared band \([s,e)\) is active without filing. A filing-triggered
band activates as \([\max(s,f_i),e)\) only when \(A_i\) holds and its start is
strictly before its expiry. Otherwise it is absent. For active support \(P_i\),

\[
G_i(\theta)=
\begin{cases}
[q_i,r)\setminus P_i(\theta),&q_i<r,\\
\varnothing,&r\leq q_i.
\end{cases}
\]

The response-first convention at equality is a model assumption. All clocks
are nonnegative integer hours from notice; all support and gaps are half open.
The exact components and their locations are retained alongside their duration.

**Conditional boundary lemma.** If \(r\leq q_i\), the represented gap is empty.
If \(q_i<r\), automatic protection gives an empty gap exactly when
\(s\leq q_i\) and \(r\leq e\). Filing protection gives an empty gap exactly
when \(A_i\), \(\max(s,f_i)\leq q_i\), and \(r\leq e\). An absent band leaves
the complete positive wait uncovered.

The proof is interval containment: a nonempty \([q_i,r)\) lies in one active
\([b,e)\) precisely when \(b\leq q_i\) and \(r\leq e\). Substitution of the two
activation rules proves the stated cases. It establishes a relation in this
model, not practical safety, political legitimacy, lawful competence or consent.

With fixed inputs and endpoints, automatic active support contains
filing-activated support, hence its gap is a subset for each person. Earlier
response with the activation and other inputs held fixed weakly reduces gap
sets. These conditional statements do not rank changing duties, appointments,
funding, expiry or jurisdictions. A zero gap can coexist with failed admission,
preparation or deadline conditions.

## Figures and exact contrasts

The readiness figure contains all 1,122 cells in six resident panels and
separate member strips. The two duty rows and three activation columns use
a common 0–24 h exposure scale. A cross marks readiness after closing even
where exposure is zero; the dashed row guide marks response at 20 h. The
member strip retains that person's fixed readiness and own activation.

The endpoint figure contains 1,200 cells at response 20 h and resident readiness
6 h: four 300-band triangles, with invalid endpoint combinations excluded.
It distinguishes an empty gap, an initial gap, a terminal gap, two components,
and the whole wait. Four two-person timelines retain source-cell identities.
Neither white nor any other colour denotes legitimacy.

Two selected comparisons use the existing exact residual-profile order,
within one duty stratum:

- Original-duty bands \([13,20)\) and \([12,19)\) each leave resident-b one
  hour, at different positions. The second also leaves member-a a terminal
  hour. The resulting profiles are incomparable; equal duration is not
  interchangeable exposure.
- Early-threat \([3,20)\) automatic protection gives the resident an empty gap.
  Filing activation at 6 h leaves \([3,6)\). Member-a's result is shown
  separately. The automatic residual profile is contained in the filing one
  for these fixed duties; no practical or normative superiority follows.

These use established H/P endpoint and activation questions as anchors.
The new contribution is their bounded sensitivity map and the visibility
of conditions that a duration alone erases.

## Regenerate a new private analytical epoch

Use the qualified locked application with its exact reviewed Blake dependency
and the supported GitVault workflow:

~~~sh
uv run --locked python -m blakean_federalism.review_timing_cli \
  --root . --output analysis_output/review-timing-atlas/new-epoch --figures
~~~

The source checkout also provides the thin
`tools.audit_review_timing` entry point. Both delegate to the same installed
package implementation. Omitting `--figures` requires no ReportLab, image or
rasterization import. The drawing path uses the existing optional manuscript
dependencies and actual Poppler rasterizer.

The producer refuses occupied, symlinked or out-of-private-root destinations.
Inputs and producer source are checked before and after export. A completion
receipt is written last. A failed raster child is reaped and retains its
PID, command, raw streams and terminal status; a partial analytical epoch has
no completion receipt. Preserve it and choose a fresh destination.

| Output | Purpose |
|---|---|
| `atlas-spec.json` | Exact consumed specification |
| `atlas-configurations.jsonl` | Every unique configuration and slice membership |
| `atlas-claimants.csv` | Both people's raw events, capacities, predicates, exact gaps, topology and four practical statuses |
| `atlas-summary.json` | Per-duty/per-mode denominators and descriptive counts |
| `atlas-selected-contrasts.csv` | Two fixed-duty comparisons, with each person's exact gap |
| `figure-data.json` | Every selected cell and both people's raw audit fields |
| `captions.json` | Captions derived from the same summary and figure selection |
| `figures/` | Vector PDF masters, PNG derivatives, registry and actual raster-child receipts |
| `atlas-receipt.json` | Input/output/source/SDK/runtime bindings and linked baseline safeguard assessments |

Hold the final receipt SHA-256 outside the run. `verify_timing_output(output,
expected_receipt_sha256)` checks its pin, exact file membership, sizes and
hashes. It is byte/custody verification, not an independent recomputation.
In figure-data JSON, native computed properties can be reconstructed from
the retained audit fields; the CSV explicitly carries all seven predicates.

The analytical receipt records the imported SDK source version/path and
installed distribution metadata separately. A source overlay can therefore
show different source and distribution identities without implying a normal
installed Git qualification. Actual process termination comes from the outer
command receipt. Root's normal installed, native manuscript, page/browser,
scholarly and publication qualifications remain separate.

## Refusing controls and remaining work

Focused checks independently enumerate the complete logical grid and derive
activation, exposure and the full seven-condition vector from original
anchor/specification inputs. They cover readiness at closing and after closing,
expiry at filing, response at/before consequence, absent/irrelevant protection,
all gap topologies, named-person reorderings and exact-set incomparability.
Capacity, admission, exit, deadline, issuer and revision controls remain outside
the atlas denominator.

Real CLI/file/process controls reject changed pins, rebound contradictory
anchors, unavailable or failed rasterizers, occupied/symlinked destinations,
changed captions, additional files and duplicate output receipts. These
establish bounded source behavior, not installed or scientific acceptance.

Main-manuscript integration must use the pinned native template with new
source/native epochs and report-derived captions. Inspect figures at their
actual page size; no page count is a target. Keep Tully's challenge to the
rules of contestation and Jerusalem's prevention/compulsion tension as
source-grounded questions, not conclusions generated by this grid. No new
reading credit, collective authorization, rights clearance, empirical effect,
accessibility acceptance or institutional warrant is supplied here.
