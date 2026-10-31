# Request-pinned review planning

Review planning prepares a deterministic workload of retrieval leads. It makes
no literary judgment and changes no reviewed/unreviewed denominator. Public
Blake owns ranking, round-robin scheduling, global unit caps, serialization and
batch verification. This application owns the original run, decision vocabulary,
eligibility and independently pinned request.

## Declared inputs

[The declared queries](../../research/review-planning-queries-v1.json)
retain exactly the seven ID/term lists from
[the existing keyword study](../../research/search-study-0.8.0.json), SHA-256
`e68405e40d0a611e47f0fb3186b4ccb4d4804ae8415607ac25f615a325cc536f`,
including the unchanged `negative_control`/`zzzxqvnegativecontrol`.
[The canonical corpus pin](../../research/corpus-pin.json) has SHA-256
`86d3f807f7258c9e29a5e498379495445faaecb3c06b9ff12720efea90dc6e98`.

The explicitly selected local input is
`local_data/corpus/blake-v0.2.0-qualified`. Read-only discovery also found the
equivalent `blake-v0.2.0` directory: both import receipts are
`8b918d7e46d14525f3a686d6032755a5ae9738f5c61f01a7ede67fffadd5c661`,
and all three retained payload hashes match the canonical pin. The qualified
path is selected explicitly; the directories are not combined.

No historical Federalism EvidenceRun or authored decision input was present
at discovery. The qualified normal-installed 0.18.0 application completed the one authorized
existing-query `prepare_review` epoch after adopting the exact public 0.5.0 SDK.
Its retained output is
`analysis_output/review-planning-20261030-01/source-run`. Retain the completed
run SHA independently before creating the request and batch; decisions must be
explicitly `null`. Never infer decisions from prose or reading ledgers.
The original keyword study and regex candidate preparation retain their distinct
matching profiles: compare declared membership, source facets and negative zeros
where comparable, and report differences rather than rebaselining old results.

The independently pinned request declares a target of 25, a retained seed,
term/source-plane/
source-role strata, exact whole-text SHA units and at most one selected candidate
per exact-text unit. The target is a request, not an achieved count. Shortfall
remains explicit. This greedy plan is neither a probability sample nor a quota
optimizer, and shared units can starve strata. Equal whole texts do not reconcile
embedded poems or establish independent copies.

Scope must be explicit: `blake_primary_reading` requires the William Blake
author ID, primary source role and reading plane together; `all_sources`
retains every original source facet. An isolated `blake_primary` flag cannot
promote or demote a witness. All supplied authored decisions are validated
against the complete original run before filtering. Only reviewed IDs inside
the selected scope become exclusions. Global and in-scope counts remain separate
in `load_planning_input`; a planned batch adds no decision.

## Plan and independently verify

Run from this application's root with the qualified locked installed SDK.
Candidate-source overlays are development evidence and do not establish that
installed qualification. The request pin must come from a trusted external
record of the declared request, separately from the batch receipt pin.

~~~sh
uv run --locked --no-sync blakean plan-review \
  --request research/review-planning-request-v1.json \
  --request-sha256 "$REQUEST_SHA256" \
  --output analysis_output/review-planning-20261030-01/batch
uv run --locked --no-sync blakean verify-review \
  --request research/review-planning-request-v1.json \
  --request-sha256 "$REQUEST_SHA256" \
  --batch analysis_output/review-planning-20261030-01/batch \
  --batch-sha256 "$BATCH_RECEIPT_SHA256"
~~~

The batch contains exactly `plan.json`, selected `hits.jsonl`, a blank
`review-queue.csv` and final `run.json`. Keep provider contexts private under
ignored `analysis_output/`; keep notes and edited queue copies outside the
immutable batch. Occupied, symlinked and source-overlapping outputs refuse.

Verification rederives the original scoped pool and exclusions from the pinned
request and complete validated decisions. It checks the full verified plan spec,
including selection and exclusions. Matching a stored context-hash string alone
cannot authorize another policy. The core verifier admits its exact files,
recomputes the plan and checks selected fields/order and unchanged blank queue;
historical producer identity remains historical.

A later contextual review binds decisions to the **original source-run SHA**
and original hit IDs, rather than substituting the planning batch receipt.
Use the existing authored-review workflow; preserve uncertainty, source roles,
repetitions, locators, disagreements and all omitted candidates. Planning does
not confer reading credit, representativeness, accuracy or scholarly acceptance.

## Qualification boundaries

Real synthetic original runs, normal JSON/CSV admission and subprocess CLI
controls cover wrong request/source/decision/batch pins, globally invalid
out-of-scope judgments, facet-based eligibility, forged valid batches with a
different full policy, blank queues and private output custody. No mock loaders
or fabricated counters are used. Source-only checks remain distinct from fresh
normal installed qualification at the exact adopted public Git pin.

This operational unit changes no corpus, vocabulary, authored decision,
manuscript, bibliography, configuration, native renderer or retained paper.

## Qualified source-run record

The source run is `analysis_output/review-planning-20261030-01/source-run`, SHA-256 `f00df8b29c14dda34dc0e2ace3c632850d8acdc685dfc45a34e9bc79cb357ede`. It scans 2,067 retained source units and contains 870 unadjudicated candidates, including 223 in the identified Blake-primary reading scope. The unchanged negative control has zero matches. No authored decision input existed; the request explicitly records `null`.

[The request](../../research/review-planning-request-v1.json) has SHA-256 `994f1e27b4d807f389fde9a6f12eb80a08d98c26c57be5e7cc22dfd36ccfa663`. Full query/facet comparisons, including zeros, are retained in `analysis_output/review-planning-20261030-01/source-comparison.json`. The casefold-literal and regex profiles remain separately labelled; this new retrieval epoch does not replace the historical keyword study or grant reading credit.

## Qualified planned batch

The normal-installed 0.18.0 application, using public Blake 0.5.0 at `36b874e76d7e0549d0ea6b9f0713ced7fb41afa8`, selected 25 candidates; shortfall is 0. The complete source run contains 870 candidates and 0 validated authored decisions; the requested scope contains 223 candidates and 0 exclusions. The selected CSV keeps every judgment field blank and the original source-run and decision bytes unchanged. No authored decision was added.

Request SHA-256: `994f1e27b4d807f389fde9a6f12eb80a08d98c26c57be5e7cc22dfd36ccfa663`. Batch receipt SHA-256: `21d6553037f09dfe3195920b59b37fac194107646173ad09cc01c3b11b6edcff`. Source-pool SHA-256: `35deeb536f96dfb18430898e51121c205dc798def8693ffa1f764cbf643193f4`. The private batch is `analysis_output/review-planning-20261030-01/batch`. Actual CLI controls reject wrong request/batch pins, occupied/source-overlapping outputs and an otherwise core-valid batch with the same context hash but a different full selection policy.
