# Local research workbench

The workbench is a portable HTML research folio, with embedded Bitstream Vera fonts, CSS, JavaScript and selected evidence. It makes no automatic network requests, stores no browser preferences and requires no server. Online source links need a connection. Raw corpus bodies, modern full-text papers and plate images are excluded.

Build from a verified independent corpus import and concordance:

~~~bash
uv run blakean build-workbench --corpus local_data/corpus/blake-v0.2.0-qualified --concordance-file analysis_output/concordance-v0.3.0.json --output analysis_output/workbench/new-run
~~~

The command defaults to [the cumulative 0.13.0 reading ledger](../research/scholarship-reading-0.13.0.json), as declared by the CLI and report builder. Use `--readings` to select a deliberate historical or alternative ledger. Earlier ledgers retain their original reading ceilings. [Project status](PROJECT_STATUS.md) records current software and paper qualifications.

Open research-workbench.html in a browser. Without JavaScript all three sections remain readable. Enhanced tabs use manual keyboard activation: arrows/Home/End move focus; Enter/Space activates. Filters match saved query names and explicit variants, not the corpus text. Clear search retains plane/role; Reset filters clears all. Native disclosures retain actual inputs and full bindings.

Coverage uses matched source units divided by all units in that plane/role. N/A means no source units; 0% in a populated category means no stored match. Repeated copies, pages and XML remain distinct. No grand multiquery coverage or freedom score is computed.

Each case shows all fifteen checks with three result states: active satisfied, active failed and condition absent. The assessment schema is version 2; historical findings-only artifacts remain in their original epoch. Label ablation compares the same programmed safeguards with poetic and national labels removed. This is a software separation control, not an empirical test of political or interpretive value.

The generator reconciles stored spans/hashes/metadata, query identities and all aggregates against the copied source index, verifies exact manuscript quotations and selected rights records, and binds consumed inputs and package resources. It refuses changed inputs, duplicate identities, inconsistent counts and unsafe/occupied destinations. Generation does not grant browser QA or independent acceptance.

Design tokens, primitives, performance budgets and verification scenarios are recorded in the [historical 0.3.0 design](history/DESIGN-0.3.0.md). The design targets accessible keyboard use, narrow screens, high contrast and zero motion; compliance claims require their own evidence.


## Statistical and counterfactual analyses

The Corpus view includes pooled/equal-family rates for all twenty queries. The companion JSON contains exact query specifications, source identities, token denominators, per-family/copy/edition strata, duplicate groups, finite deletion results and three association universes. The Cases view lists each minimum safeguard bundle alongside the baseline action and fixed material context. Twelve operators create 4,096 subsets per baseline; repeated resulting records are counted separately from declared subsets.

Use corpus-statistics and experiment-cases to export either analysis independently. Outputs must be new ignored analysis_output paths. Both commands run without manuscript rendering dependencies. The former verifies the imported corpus; the latter retains all changed field paths and replacement values in its catalog. [Corpus definitions](research/corpus-statistics-0.6.0.md) and [experimental definitions](research/institutional-experiments-0.6.0.md).

The HTML embeds a compact manifest that binds the complete companion JSON by SHA-256. All reading views, filters, cases and source records remain in the HTML; detailed statistical strata stay in the JSON, with no automatic file or network retrieval. The raw HTML budget remains 768 KiB.


## Search beyond saved groups

Use the separate [local fulltext workspace](corpus-search.md) for arbitrary words and phrases. It searches all imported units with role/plane/family filters, retains exact source spans and compares source-family coverage before the display cap. The aggregate workbench remains compact and distributable only within the selected author-approved distribution scope; fulltext search and result contexts stay local and ignored.
