# Corpus statistics: repetition, normalization and source-family sensitivity

The new computation analyzes the 199 primary reading units in the copied, qualified corpus. They contain 644,245 Unicode word tokens and carry 33 distinct `work_id` values. Each primary unit is a source-file/copy extraction. The inventory also retains all 1,868 excluded editorial or unverified units in its source census and source fingerprint.

## Results that change the interpretation of the retrieval counts

Exact-text deduplication removes one repeated America copy n extraction: 199 units become 198, and 644,245 tokens become 641,304. The duplicate IDs are `archive:america.n` and `archive:america.n--878c90904184`; both have text SHA-256 `8eeb3ebfb7cad1536fe712b537662d8c044ab15836311271ee7b07658727d2c2`. This control changes the state/states query from 264 to 263 occurrences and from 4.09782 to 4.10102 occurrences per 10,000 tokens. Here the repeated copies of different texts matter much more than the one exactly repeated extraction.

The equal-source-family state rate is 3.48624 per 10,000 tokens, compared with the pooled rate of 4.09782. Its leave-one-family-out rates span 3.45440–4.42767. The lower endpoint omits `urizen`; the upper endpoint omits `songsie`. Urizen supplies 49 occurrences across seven copies, at 22.42460 per 10,000 tokens. Jerusalem supplies 101 across five copies, at 5.11237; Milton supplies 64 across four, at 8.42260. Jerusalem provides the largest count, while Urizen has the highest state rate of these three families. This makes the study's close reading of Milton and Jerusalem a thematic selection rather than a simple selection of the largest normalized frequency.

The person/identity query occurs 87 times in eleven units across four source families: Jerusalem (58), Milton (26), An Island in the Moon (`bb32`, 2), and All Religions are One (`aro`, 1). The nation/people query occurs in all four of those families, while the state query occurs in three. At work-ID presence level, nation/people and state share nine of seventeen families in their union (Jaccard 0.52941; lift 1.75740). Person/identity and state share three of fourteen (Jaccard 0.21429; lift 1.90385). These two comparisons answer different questions: the former has broader shared coverage; the latter shows a narrower overlap relative to the smaller person/identity set.

Concentration is particularly strong for emanation and particulars. Jerusalem supplies 380 of 418 emanation occurrences (90.91%) and 76 of 88 particular/particulars occurrences (86.36%). Removing Jerusalem reduces their pooled rates from 6.48821 to 0.85071 and from 1.36594 to 0.26865 per 10,000 tokens. The corresponding full-corpus equal-family rates are 0.73441 and 0.19414. Albion provides another useful contrast: 1,602 of its 1,982 occurrences belong to Jerusalem (80.83%), and its pooled/equal-family rates are 30.76469/5.78161. This is a textual concentration result with a direct research use: additional passage comparisons for these terms should actively seek the smaller supporting families rather than accumulating more Jerusalem copies.

The exchange/interchange query retrieves seven occurrences in seven units: four in Jerusalem, two in Milton and one in Ahania. Its pooled rate is 0.10865, while its equal-family rate is 0.20482. Equal-family weighting can therefore increase as well as decrease a rate. It does not merely penalize large books. The complete CSV gives all twenty query groups, including the zero-hit control.

## Formal definitions for numbered manuscript statements

Let $U$ be the finite set of primary reading units; let $W$ be the set of their recorded work IDs. For unit $u$, $t_u$ counts Python Unicode `\w+` tokens. For explicit query group $q$, $c_{uq}$ counts left-to-right, non-overlapping, case-insensitive whole-word matches of its literal variants. Put $h_{uq}=1$ when $c_{uq}>0$, and zero otherwise.

For any nonempty subset $S\subseteq U$, the token-normalized rate and unit coverage are

$$R_q(S)=10^4\frac{\sum_{u\in S}c_{uq}}{\sum_{u\in S}t_u},\qquad C_q(S)=\frac{\sum_{u\in S}h_{uq}}{|S|}.$$

A zero token denominator produces an undefined rate (`null`), and an empty subset produces undefined coverage. A positive denominator with no matches produces zero. For phrase variants, the numerator counts phrase occurrences and the denominator still counts word tokens.

Let $U_w=\{u\in U:work(u)=w\}$ and $W_+=\{w:\sum_{u\in U_w}t_u>0\}$. The equal-family rate and coverage are

$$\overline R_q=\frac{1}{|W_+|}\sum_{w\in W_+}R_q(U_w),\qquad \overline C_q=\frac{1}{|W|}\sum_{w\in W}C_q(U_w).$$

The report explicitly records `rate_work_groups=|W_+|`. All 33 actual families have positive token totals. The family sensitivity collection is the full list $\{R_q(U\setminus U_w):w\in W\}$, with each omitted family, remaining denominator and count retained. Minima and maxima are finite-deletion ranges, not sampling intervals.

For total occurrences $n_q>0$, the family occurrence share is $s_{wq}=\sum_{u\in U_w}c_{uq}/n_q$. The maximum share $\max_w s_{wq}$ and concentration $H_q=\sum_w s_{wq}^2$ summarize how much the pooled count depends on particular families. Both are undefined when $n_q=0$.

For a specified universe of units, let $A_q$ be those containing at least one query match. For queries $q,r$, the report computes

$$J(q,r)=\frac{|A_q\cap A_r|}{|A_q\cup A_r|},\quad P(r\mid q)=\frac{|A_q\cap A_r|}{|A_q|},\quad L(q,r)=\frac{N|A_q\cap A_r|}{|A_q||A_r|}.$$

All three values retain their denominators. An empty union gives undefined Jaccard. A zero conditioning set gives undefined conditional prevalence; a zero marginal gives undefined lift. A nonempty denominator with zero intersection gives zero. The analysis repeats every pair in three universes: 199 retained primary units, 198 exact-text representatives, and 33 source-family presence sets. In the last universe a family is present when any of its units contains the term. These are whole-unit associations; they do not count near-neighbor words.

Exact-text representatives retain the lexically first passage ID for each identical primary text digest. All member IDs of repeated groups remain in `exact_duplicate_groups`. There is no whitespace, spelling, case or OCR normalization in this sensitivity analysis.

## Grouping, variants and source identity

The 33 recorded work IDs are source-family identifiers. They are not a claim of 33 uniform, independently sampled literary works. In particular, `bb134` groups 39 distinct receipt extracts; `urizen` groups the title variants The First Book of Urizen and The Book of Urizen. Work strata retain every distinct recorded title, member passage ID and original copy/edition grouping. Copy strata use `(work_id,copy_id)` and edition strata use `(work_id,edition_id)`, so missing or reused copy labels cannot merge different families. The actual strata total 430: 33 work-ID, 199 edition and 198 copy groups.

The report embeds all twenty exact query specifications. In particular, `nations` includes nation, nations, people and peoples; `persons` includes individual, individuals, identity and identities. These broader search labels must be explained in figure keys. The search semantics match the original concordance: literal case-insensitive variants with Unicode word boundaries, longest alternatives first. A query for state does not count statement, statesman, state2, state_, or éstate. A variant group can include state and states explicitly.

The new `source_sha256` binds a canonical JSON serialization of **all** supplied Passage records, ordered by passage ID, including metadata, plane/role and full text. The report does not embed the source texts. Its `query_sha256` uses the existing `query_fingerprint` function on queries sorted by query ID. This canonical order is a new epoch and differs from the old concordance's supplied-order fingerprint. The two receipts remain separate. Changing an editorial unit also changes the input source fingerprint, although that unit contributes no primary count.

## APIs, files and figure guidance

Public entrypoint:

```python
from blakean_federalism.corpus_statistics import analyze_corpus
report = analyze_corpus(passages, queries)
```

`CorpusStatistics` and component models live in `corpus_statistics_models.py`. Aggregation helpers live in `_corpus_statistics_core.py`; all three modules belong in producer bindings. The package needs no new dependency. The report is frozen and JSON serializable; it contains no manuscript/rendering imports.

The data payload includes 199 source-unit inventories, 430 strata, 20 query summaries, 660 omission records and 570 pairwise records (190 pairs times three universes). The pretty-printed JSON is 3,276,624 bytes. Root should check the compressed and actual embedded workbench budgets after integration rather than assuming this file has the cost of the prior summary alone.

For a rate plot, use black for pooled rates and red for equal-family means; label the unit “occurrences per 10,000 Unicode word tokens.” A separate interval shows the complete leave-one-family-out range with its deletion meaning stated directly. It is not an error bar around the equal-family mean. For the association matrix, use `work_presence`, label a selected Jaccard cell with its intersection/union as space allows, and give the 33-family universe. Display the zero-hit control as zero or undefined as mathematically appropriate rather than omitting its row silently.

Candidate rate caption: “Primary-text retrieval after token normalization and source-family balancing. Pooled rates use 644,245 tokens across 199 source units. Red values average the 33 work-ID family rates; the complete family-deletion ranges show how removing one family changes the pooled rate. Query variants are fixed in the analysis specification.”

Candidate association caption: “Term-group overlap across 33 recorded source families. Cells show Jaccard overlap of family-presence sets; each family counts once regardless of its number of copies. The nation/people and state groups overlap in nine of seventeen families in their union; person/identity and state overlap in three of fourteen.”

## Qualification and retained controls

`initial-red.log` records the test collection failure before the new module existed. `focused-tests.log` records 21 passing tests with 100% line and branch coverage for the three new modules. The oracles use hand-counted finite texts, duplicate copies, grouped editions, Unicode boundaries, longest phrase variants, zero tokens, zero matches and independent set ratios. Seven malformed query/membership configurations and four blank group identity controls raise real `ResearchError` exceptions. Tests use no mocking framework.

`lint-final.log` records clean Ruff checks; `typing-final.log` records zero strict BasedPyright errors, warnings or notes. `analysis-receipt.json` binds the exact three sources, tests, queries, corpus pin, SQLite file, original concordance and result JSON. A fresh complete recomputation equals the saved report, and all twenty primary occurrence/matched-unit pairs exactly agree with the preserved original concordance. The negative-control query and every corresponding pair intersection remain zero.

No upstream data, manuscript, figure, CLI, existing model, dependency, release or Git state was changed by this worker. Root's integrated full-suite, visual and release qualification remain separate.
