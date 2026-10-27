# Corpus-wide search

Search the independently imported, hash-pinned SQLite projection with arbitrary literal words or phrases. This complements the twenty saved analytical groups; it does not replace their original producer receipts.

~~~bash
uv run blakean search-corpus --term "minute particulars" --output analysis_output/phrase.json
uv run blakean search-corpus --term liberty --term freedom --output analysis_output/alternatives.json
uv run blakean search-corpus --term state --term individual --mode all --work-id milton --output analysis_output/conjunction.json
uv run blakean search-corpus --term state --term individual --mode all --window-words 20 --output analysis_output/window.json
uv run blakean search-corpus --term nation --all-sources --plane erdman --output analysis_output/editorial.json
uv run blakean build-search-workspace --output analysis_output/corpus-search/new-run
uv run blakean search-study --output analysis_output/search-study.json
~~~

The default corpus and pin come from local_data/corpus/blake-v0.2.0-qualified and research/corpus-pin.json. Every input checksum is revalidated before search. Primary text is the default; --all-sources includes editorial and unverified units. --role selects one role, --plane one source plane, and --work-id one recorded source-family ID. Contradictory role options are refused. Recorded work IDs are source families, not a critical work catalogue.

Terms are literal, casefolded Unicode text. Regex metacharacters remain literal. Phrases preserve whitespace and punctuation; a phrase crossing a source line break requires that line break. --substring removes word-boundary requirements. Casefold expansions map back to complete original characters: STRASSE matches Straße, but a single s cannot match half of ß. Accents are retained. Offsets use original Unicode codepoints, not browser UTF16 units. Every term matches nonoverlapping spans independently. Distinct overlapping terms have separate labeled matches. Any accepts at least one term; all requires every term within one stored source unit, which can span an entire poem.

JSON retains the complete counts and source-family facets, while --limit bounds returned contexts to 1–1,000. Each hit includes its source identity, role, plane, edition, locator, source URL, rights label, text SHA-256, original span and context bounds. Facets include zero-match eligible families and token denominators. Counts are computed before the display cap. --context-chars controls the retained surrounding text, from zero to 500 characters per side.

The standalone workspace includes all imported full texts locally, supports the same literal-query semantics, shows family distributions and role/plane counts, and exports the current result JSON. Open its index.html directly. Full-text files and result contexts must stay under ignored analysis_output; do not attach the search workspace to a source release or redistribute it as the aggregate evidence workbench. The workspace receipt binds payload/output hashes, Unicode tables and the corpus pin. Existing outputs and symlinks are refused.

The seven-query search study exports only aggregate counts/facets and query specifications. It contains no source bodies or contexts. The manuscript figure is rebuilt from research/search-study-0.8.0.json, whose corpus pin must match the publication corpus.

## Optional word-window ALL

`--window-words W` (JSON `window_words`) accepts an integer from 1 through 200 only with `mode="all"` and at least two distinct casefolded terms. ANY, a single term, repeated casefold aliases, booleans, fractional values and out-of-range values are rejected. No mode is silently changed. Omit the option, or use JSON null, to retain the existing document-level ANY/ALL behavior.

A complete window chooses one existing literal match of each term in one stored source unit. Its envelope is the half-open original-codepoint interval from the earliest start to the latest end. Its cost is the number of original-text `\w+` runs intersecting that envelope, using Python Unicode alphanumeric/underscore membership. The window qualifies if that count is at most W. Phrase tokens count toward W; underscores stay within a token; whitespace and punctuation separate tokens. A punctuation-only envelope can cost zero. Substring matches touching part of a word count that word. Terms can overlap or nest; matching remains nonoverlapping per term and does not invent additional matches or pair a term with itself. Exact whitespace, casefold expansion alignment and original offsets are unchanged.

Each occurrence is counted once if it participates in at least one qualifying complete window. Nearby occurrences of only a subset of terms do not qualify. For example, `a x b` qualifies at W=3 and fails at W=2, while document ALL still succeeds. `a b c` with terms `a b` and `c` needs W=3. With substring matching, the three distinct terms `ab`, `aba`, `ba` all qualify in the single token `aba` at W=1. No cross-source-unit window is formed.

All occurrence totals, matched-unit counts, facets and token-normalized rates use only qualifying occurrences before the returned-hit cap. Eligible-unit and token denominators remain the entire filtered corpus. The browser's optional Word window control, result label, status and exported request preserve the selected W. Clear resets to document search.

The implementation sweeps intervals of feasible integer window origins and tests each match for intersection with all-term coverage. For H literal matches and T original tokens in a source unit, the window step uses O(T + H log T + H log H) time and O(T + H) memory, in addition to the existing literal scan. It does not enumerate Cartesian products. Window mode necessarily retains all candidate spans before filtering; the display cap is not a memory cap. Large source units or very frequent substring terms can use more memory and block the synchronous offline browser while searching. No semantic similarity or linguistic normalization is applied.

The request field is additive: historical requests/results without `window_words` still read as null. New serialized requests include `"window_words": null` by default; their complete JSON bytes therefore differ from older serialization. Existing document-level counts, facets, hit spans and ordering remain unchanged. The retained `research/search-study-0.8.0.json` is historical evidence and is not rewritten by this addition.


## Compare near and document-wide combinations

`uv run blakean proximity-study --output analysis_output/proximity-study.json` recomputes the fixed six-pair grid across 8, 16, 32 and 64 original word tokens and document-wide ALL. The command verifies the pinned 2,067-unit import and the historical aggregate's primary family strata before measuring the grid. Output contains counts, denominators, family facets and normalized rates, with no source contexts. The committed research/proximity-study-0.10.0.json records this comparison; research/search-study-0.8.0.json remains the earlier literal-search aggregate.

All participating occurrences count once before the display cap. A term's distant occurrences are excluded unless they participate in another complete qualifying combination. For an actual nearby passage, use `search-corpus --term state --term individual --mode all --window-words 32 --output analysis_output/state-person-near.json` or enter the same terms and word window in the local offline search workspace.
