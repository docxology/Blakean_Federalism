# Published edition and verification

The author-approved edition is published at [Zenodo](https://doi.org/10.5281/zenodo.23900617)
and [v1.0.0](https://github.com/docxology/Blakean_Federalism/releases/tag/v1.0.0). The [actual publication receipt](../research/publication-20261103.json)
binds tag/source, registered DOI, assets, normal installations and anonymous
download checks. All eight assets match SHA-256 and size on both services.
The PDFs retain their approved bytes. Source, software, native output,
scholarly judgments and publication remain separate claims.

The release tag selects the immutable source map deposited beside its assets.
This later documentation closure records completed events without changing
that tag, paper, software version, SDK selection or analytical producer.

## Public clone: an explicit source-only profile

Keep source, both Python prefixes, caches and TMP on mounted GitVault
when working in this collection. From the repository root, select the
qualified interpreter and a normal installation:

~~~sh
uv sync --locked --no-editable --python 3.15.1 --extra manuscript
uv run --locked --no-sync blakean --help
uv run --locked --no-sync pytest tests/test_publication_source_closure.py -q
~~~

This profile passed **3 tests** against a source-only snapshot
with neither local_data/ nor analysis_output/, using the new canonical
Public installation. It includes real admission/refusal checks. It is
a bounded profile, not the full suite or a coverage-floor result.

## Full research qualification needs retained fixtures

The complete installed suite passed **821 tests** with the authorized
retained data available in the Public canonical checkout. Running all
tests in a source-only clone also selects corpus, reference-source,
casebook/image or prepared-output fixtures that are intentionally absent
from Git. Missing-fixture errors are not a successful qualification.
Restore only the independently pinned, lawfully held inputs described
in [project status](PROJECT_STATUS.md), [corpus custody](../PRIVACY.md)
and the [native guide](manuscript/README.md) before the full gate. Do not
silently skip errors, substitute new downloads, or change a corpus pin.

## Rendering and remaining research

The rendering-input ZIP preserves original native inputs, selected
attributed figures and approved HTML, including its then-private status
metadata. Its verifier checks declared member bytes and refuses changes.
It is an inspection-input bundle, not a new native replay or a public
analytical corpus. The pinned docxology/template APIs, installed SDK
admission and authorized inputs remain necessary for new production.
[Distribution terms](../LICENSE-PAPER.md) preserve reserved authored
research rights and third-party notices. Publication adds no adjudications,
whole-oeuvre/image census, peer review or accessibility certification.

## Later source maintenance

[Maintenance guidance](maintenance.md) and [dated documentation bindings](../research/documentation-maintenance-20261103.json)
identify post-release source changes. The fixed release tag and deposited
rendering inputs retain their original producer and qualification.

## Pinned Template source-only check

This check reads only the tracked publication record, PDF, and overview SVG. It
confirms the PDF checksum, byte length, and physical page count, then stages a
raster copy of the overview for a short explanatory fixture. It requires Python
3.11 or later, Poppler's `pdfinfo`, and Inkscape. Run from the repository root.

~~~sh
stage_root="$(mktemp -d)"
federalism_stage="$stage_root/Blakean_Federalism"
python docs/examples/Blakean_Federalism/prepare.py "$federalism_stage"
~~~

Use a separate [Template checkout](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2) at
`87704feae0a4490ef7dad9c931d268e8c30273c2`. Install its Pandoc,
pandoc-crossref, and LaTeX prerequisites as described in the
[Template run guide](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/docs/RUN_GUIDE.md).
In the same shell, move to the Template checkout and run the following with an
unused project slot. The preparation command copies the verification note into a
disposable project and indexes those staged inputs for provenance.

~~~sh
uv sync --locked --no-dev
mkdir -p projects/working
ln -s "$federalism_stage" projects/working/Blakean_Federalism
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/Blakean_Federalism --skip-manuscript-hydration
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/Blakean_Federalism
~~~

The fixture writes its PDF, HTML, and reports under
`$federalism_stage/output/`. The article itself uses the
[qualified native workflow](manuscript/README.md) and a different recorded
Template revision. The fixture does not hydrate article values, recreate
source images, or replace the published edition.
