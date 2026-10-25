# Local research workbench

The workbench is a portable HTML research folio, with embedded Bitstream Vera fonts, CSS, JavaScript and selected evidence. It makes no automatic network requests, stores no browser preferences and requires no server. Online source links need a connection. Raw corpus bodies, modern full-text papers and plate images are excluded.

Build from a verified independent corpus import and concordance:

~~~bash
uv run blakean build-workbench --corpus local_data/corpus/blake-v0.2.0-qualified --concordance-file analysis_output/concordance-v0.3.0.json --output analysis_output/workbench/new-run
~~~

The command uses the package’s current reading ledger (`research/scholarship-reading-0.5.0.json` in this version). Use `--readings` only to select a deliberate historical or alternative ledger.

Open research-workbench.html in a browser. Without JavaScript all three sections remain readable. Enhanced tabs use manual keyboard activation: arrows/Home/End move focus; Enter/Space activates. Filters match saved query names and explicit variants, not the corpus text. Clear search retains plane/role; Reset filters clears all. Native disclosures retain actual inputs and full bindings.

Coverage uses matched source units divided by all units in that plane/role. N/A means no source units; 0% in a populated category means no stored match. Repeated copies, pages and XML remain distinct. No grand multiquery coverage or freedom score is computed.

Each case shows every one of fifteen checks, including conditional nonviolations. The assessment schema is version 2; historical findings-only artifacts remain in their original epoch. Label ablation compares the same programmed safeguards with poetic and national labels removed. This is a software separation control, not an empirical test of political or interpretive value.

The generator reconciles stored spans/hashes/metadata, query identities and all aggregates against the copied source index, verifies exact manuscript quotations and selected rights records, and binds consumed inputs and package resources. It refuses changed inputs, duplicate identities, inconsistent counts and unsafe/occupied destinations. Generation does not grant browser QA or independent acceptance.

Design tokens, primitives, performance budgets and verification scenarios are recorded in DESIGN.md. The design targets accessible keyboard use, narrow screens, high contrast and zero motion; compliance claims require their own evidence.
