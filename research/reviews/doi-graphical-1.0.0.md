# Independent gate review

recommendation: APPROVE
verdict: APPROVE_FOR_PRIVATE_AUTHOR_REVIEW
blockers: []
scope: Exact frozen unpublished software/PDF/HTML candidates only. No scientific, public-rights, accessibility, hosted-CI, or release approval.

## Original intent and desired outcome

The user requested actual reserved Zenodo DOIs on both covers, richer source-linked graphical abstracts, smaller PDF margins, and review PDFs delivered to Downloads before final approval of any public action. This leaf gate evaluates readiness of the two immutable candidates for that private author review. Private-main integration and Downloads delivery are explicitly later parent-owned events, not outcomes claimed here.

Both editions satisfy that bounded outcome: authentic/source-identified cover imagery, three distinct enriched graphical pages after the cover, contents beginning on physical page 5, restrained interpretation, visible source/copy distinctions, and usable smaller-margin layouts. DOI reservations are real retained production API records, unsubmitted with zero files, not registered public deposits. No network/API re-query was authorized or performed.

## Exact identities

| Candidate | Source map | PDF SHA-256 | HTML SHA-256 | Pages |
|---|---|---|---|---|
| Entomology 1.0.0 | 1d9478a9792cbf4e2f7c381d8724207158754506e38f0a06e2cd1f8c038d15c2 | fc99a3dd629646a6e7cb1b41e0b6290388cbb4a09d7c0f91526e0c413dddf73a | 7f36f6a36b3a3f319d9fb1ecedbcd71b23897dcdb8591fabd89e3a3e927af4af | 42 |
| Federalism 1.0.0 | 2b5b2e89360b3bdd8932d3b7d0a8773e71941cd8d808279c46f9618ed9939679 | 14be777acc438a12b0b0077fe26aa0d0c57e7d8505274dfa30c3c1f05e809c52 | 1f8e94c8aae84fb4bfee85163bd3086d7ab2cf35947cad0f5b294913a9c877b1 | 76 |

Source maps cover 302 and 437 members. Independently recomputed before and after, all declared changed paths match, and both native/canonical-candidate PDF copies have the selected identity. Exact paths are in binding-before.json, binding-after.json and the parent coordination/REVIEW-INPUTS.json. Frozen baseline commits are 773667deab8e24411f2d3801e59ac56a8275d2d7 and 216a9a4362a8c27af072bbe5eade9b1ab455f53e. No Git command was used or commit qualification inferred.

## Criterion and QA matrix

| ID | Required outcome / scenario | Observation | Evidence |
|---|---|---|---|
| C1 | Mounted external custody; guidance precedes semantic work | First command asserted mount and physical prefixes; environment bindings on every logged command. GUIDANCE_COMPLETE recorded before brief read. Only review root written. | GUIDANCE_COMPLETE.json; evidence/001-guidance through 009-brief |
| C2 | Exact immutable source/native bindings | All 739 source-map members, changed-path hashes and PDF/HTML hashes match before/after. Native receipts bind 1626 template source members each; all recomputed. | binding-before.json; binding-after.json; native-closure.json; evidence/013,023,041 prefixes |
| C3 | Actual normal-installed software and SDK | Application source/runtime equality: 45/106 members; actual app RECORD verification: 55/116 hashed members; noneditable direct_url. Public SDK verifier validates 163 members and exact Git pin 263d7c83abe6f1309a64af3285a683c1b7672269. Both physical prefixes external. | entomology-installed.json; federalism-installed.json; evidence/016-* |
| C4 | Bounded tests plus refusing controls | Entomology 10 and Federalism 16 targeted tests pass with warnings as errors, no coverage writes, Q-only caches/basetemp. Wrong installed Git pin refused in both environments. Undefined composition, missing shares and forged producer/version/output cases exercised in targeted tests. | evidence/014-*; evidence/016-* |
| C5 | Retained full software gates are credible | Read actual raw full-suite outputs and terminal receipts: 474/821 pass. Independently aggregated raw coverage JSON: E 2854/3134=91.0657% app,1012/1503=67.3320% tools; F 4885/5300=92.1698%,361/523=69.0249%. Current lint and types report clean. Full suites not rerun. | evidence/017-raw-gates;018-gate-results; parent evidence/075-entomology-v1-full-regression,098-federalism-v1-final-full-regression,072-entomology-v1-types,094-federalism-guard-types |
| C6 | Actual PDF cover, layout and every physical page | All E1–42 and F1–76 visually examined in complete contact-sheet sequence; enlarged openings and selected dense/changed pages separately examined. Independent extraction confirms all words within letter trim, correct titles/author/DOI annotations, TOC on page5 and no unresolved braces/??. | pdf-independent.json; evidence/024-*,027-pdf-structure; parent artifacts/*-allpages |
| C7 | Source/image/caption/citation/formalism and graphic joins | E67 stage inputs and nine request pins match; all four opening images exactly match PDF embedded pixels. F136 prepared source inputs,60 figure assets,40 quotation occurrences,23 formalism blocks,15 equations,33 body figure labels and60 bibliography keys revalidated through actual installed read-only checks. F opening images pixel-identical. | reference-image-joins.json; evidence/033-reference-image-joins |
| C8 | Exact HTML has actual browser evidence | Checked owner browser scripts, raw records, closure receipts and desktop/mobile screenshots for final exact paths. 18 E /37 F images load at both widths with preserved aspect ratios, no duplicate/missing anchors, no root overflow,74/265 math nodes without errors. Tables use local scrolling where needed. | evidence/022,023,028,041 prefixes; parent artifacts/browser-owner02 and browser-owner01 |
| C9 | Historical failures and semantic limits preserved | Independently rejected old native01 footer:41 page numbers reach yMax792.639744 beyond792pt; current bounds pass. Exactly four old/current HHI differences, each1ULP; all other domain fields equal apart from producer identity. Exact rational recomputation retained. | footer-refusal.json; domain-diff.json; rational-and-graphic-values.json; evidence/035,036,039,040 prefixes |
| C10 | Status separates reservation/review/delivery/publication | Both status pages, manuscript guides and publication plans identify unpublished reservations, later private-main/Downloads events, and held public actions. 36039/47/35992 E denominator and incomplete image/Baine readings remain explicit. | source/{entomology,federalism}/docs/PROJECT_STATUS.md,docs/manuscript/README.md,docs/publication-plan.md,research/review-candidate-1.0.0.json |

Commands are recorded exactly, with cwd, executable, argv, selected storage controls, PID, raw stdout/stderr and completion, in each evidence directory's prelaunch.json, pid.json, stdout.log, stderr.log and completion.json. The numeric prefixes above identify unique retained evidence directories.

## Physical and browser review coverage

All PDF pages were inspected for layout via these actual view_image contact sheets:
- Entomology:001–009,010–018,019–027,028–036,037–042.
- Federalism:001–009,010–018,019–027,028–036,037–045,046–054,055–063,064–072,073–076.

Enlarged individual current PDF pages: E2,3,4,21,22,23,39; F1,2,3,4,7,31,51,68. These include new graphics, corrected edition signposts, mathematical definitions/equations, dense tables and reading/rights appendices. All-page overview is layout inspection, not a claim to have read all scholarly prose or all reproduced original text. The complete images are preserved and distinguish copy/edition/plate numbering. F source-omission intervals independently recompute to states3.45–4.43/pooled4.10 and imagination1.25–2.31/pooled2.03, matching the enlarged graphics. E review bar uses47/36039 rather than enlarging it; no visual implication that the remainder was reviewed.

Browser screenshots viewed: E desktop figures01,03,18 and mobile02,03; F desktop02,03,04 and mobile02,04,23. Desktop text/figures are clear; mobile dense graphics require their visible full-size links. DOM/table/math evidence was inspected for both viewports. No fresh browser was launched; the inspected owner's sessions have normal-close receipts. This is not specialist accessibility or interactive math-tool qualification.

## Direct programming and remove-ai-slops pass

Consulted both skills and directly reviewed changed production code, the source-bound diff and new/modified tests. Retained diffs are entomology-code.diff and federalism-code.diff, produced without Git by verifying original-file hashes against the baseline before comparing bytes.

No excessive/deletion-only/removal-pinning or natural-language-prose tests were introduced. Entomology's tests distinguish0/25/100% pixel geometry, empty populations and undefined category shares with actual PIL output. The Federalism provenance regression performs real child execution and real file mutations; the old report/receipt hashes remain unchanged, and the producer version is compared to independently installed distribution metadata. The retained RED shows the forged version was accepted before the guard, and GREEN plus this independent targeted run show refusal now. No mocking frameworks were introduced.

Nonblocking test-quality note: Federalism test_abstract_sensitivity_inset.py counts four PDF curve operators per point, coupling that assertion to ReportLab's circle representation, and tests label presence rather than exact interval geometry. It gives narrower confidence than a geometric assertion. This does not violate the stated candidate outcome: actual final graphics were independently inspected and their displayed source-omission values recomputed. It is not treated as proof of general future geometry correctness.

Production helpers are small domain visualization units, not generic algorithms moved into applications. Existing admitted typed reports supply the data; no new parsing/normalization layer, network path, swallowed errors, speculative compatibility layer or side-effectful fallback was added. Zero-axis fallback in F supplies a drawing scale only, not a fabricated estimate; undefined estimates retain unavailable labels. All changed Python modules are <=229 pure lines; analytical_abstracts.py is in the200–250 warning band. New detail/inset modules have105/55 pure lines. No size criterion fails.

No separate current code-review report explicitly documenting both skill perspectives was found in the packet's review/evidence locations. The raw code/gate evidence and this direct pass supply that coverage; absence of a duplicate report is not a criterion violation.

## Preserved failures and procedure exceptions

- evidence/025-pdf-structure: ModuleNotFoundError for pypdf in the Entomology environment. No installation attempted. The identical check was retained in Q and passed under the already installed Federalism environment in027.
- evidence/035-domain-invariance: the reviewer's assertion incorrectly expected the string concentration in an actual path named work_occurrence_hhi. The raw comparison already exposed exactly the four expected differences. Corrected only the reviewer assertion in036; no report/data/source changed.
- evidence/037-ulw-status: ULW_LOOP_PLAN_MISSING. No plan created. Required fallback gate artifact is under this exclusive review root at .omo/evidence/doi-graphical-review-gate-review.md.
- An overbroad read-only report-name enumeration in020 traversed retained packet subdirectories and took longer than intended; it reached normal completion and no files were changed. No report availability claim depends on that listing.
- Initial large guidance/log outputs exceeded tool display limits; relevant guidance was reread in smaller passes and raw full streams are retained. No substantive source was opened before the recorded guidance-complete boundary.
- Parent historical failures, including forged-version RED082, clipped-footer native01 and strict domain comparison117, remain retained. None is relabelled as a successful edition.

## Exact remaining evidence gaps and limits

No blocking gap remains for this bounded private-author-review artifact gate. Downloads delivery, canonical integration/consumer identity and remote-private state are not yet established by this report; the parent must close those actual later events without changing approved product/source bytes. DOI public resolution is intentionally not asserted. Full-source scholarly correctness, all-reading credit, specialist accessibility, hosted CI, public redistribution rights, final author approval and public Zenodo/GitHub/core releases remain outside approval.

No source/native/install/Git/network modification or child agent was performed by this reviewer. All owned commands reached terminal completion; no owned browser exists. The final evidence manifest binds reviewed outputs, source selections, visual evidence and reviewer receipts, excluding its own self-hash and the active manifest-writing command's completion receipt.
