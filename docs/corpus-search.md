# Corpus-wide search

Search the independently imported, hash-pinned SQLite projection with arbitrary literal words or phrases. This complements the twenty saved analytical groups; it does not replace their original producer receipts.

~~~bash
uv run blakean search-corpus --term "minute particulars" --output analysis_output/phrase.json
uv run blakean search-corpus --term liberty --term freedom --output analysis_output/alternatives.json
uv run blakean search-corpus --term state --term individual --mode all --work-id milton --output analysis_output/conjunction.json
uv run blakean search-corpus --term nation --all-sources --plane erdman --output analysis_output/editorial.json
uv run blakean build-search-workspace --output analysis_output/corpus-search/new-run
uv run blakean search-study --output analysis_output/search-study.json
~~~

The default corpus and pin come from local_data/corpus/blake-v0.2.0-qualified and research/corpus-pin.json. Every input checksum is revalidated before search. Primary text is the default; --all-sources includes editorial and unverified units. --role selects one role, --plane one source plane, and --work-id one recorded source-family ID. Contradictory role options are refused. Recorded work IDs are source families, not a critical work catalogue.

Terms are literal, casefolded Unicode text. Regex metacharacters remain literal. Phrases preserve whitespace and punctuation; a phrase crossing a source line break requires that line break. --substring removes word-boundary requirements. Casefold expansions map back to complete original characters: STRASSE matches Straße, but a single s cannot match half of ß. Accents are retained. Offsets use original Unicode codepoints, not browser UTF16 units. Every term matches nonoverlapping spans independently. Distinct overlapping terms have separate labeled matches. Any accepts at least one term; all requires every term within one stored source unit, which can span an entire poem.

JSON retains the complete counts and source-family facets, while --limit bounds returned contexts to 1–1,000. Each hit includes its source identity, role, plane, edition, locator, source URL, rights label, text SHA-256, original span and context bounds. Facets include zero-match eligible families and token denominators. Counts are computed before the display cap. --context-chars controls the retained surrounding text, from zero to 500 characters per side.

The standalone workspace includes all imported full texts locally, supports the same literal-query semantics, shows family distributions and role/plane counts, and exports the current result JSON. Open its index.html directly. Full-text files and result contexts must stay under ignored analysis_output; do not attach the search workspace to a source release or redistribute it as the aggregate evidence workbench. The workspace receipt binds payload/output hashes, Unicode tables and the corpus pin. Existing outputs and symlinks are refused.

The seven-query search study exports only aggregate counts/facets and query specifications. It contains no source bodies or contexts. The manuscript figure is rebuilt from research/search-study-0.8.0.json, whose corpus pin must match the publication corpus.
