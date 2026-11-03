# AGENTS.md — `src/`

**Audience:** agents editing the installable application package.

`src/blakean_federalism/` is the application: it owns the Federalism argument, the political
vocabulary, the institutional models and the authored readings, and it calls the shared,
pinned methods in `blake` for corpus custody, literal retrieval and portable schemas. Its own
`__init__.py` states the ceiling that governs the whole tree — *source-bound exploratory
research, with no automatic political legitimacy inference* — and no amount of passing
software lowers that.

The reader's view is [README.md](../README.md). The repository contract is
[the root guide](../AGENTS.md); the software state and the scoped next work are
[project status](../docs/PROJECT_STATUS.md), and the shared-methods boundary is
[shared methods](../docs/shared-methods.md). Read those before this file.

## Rules

- **Upstream the reusable part.** A change to a shared method goes to `blake` and arrives here
  as a qualified pin. Do not re-implement custody, retrieval or schema conversion in this tree.
- **Keep the warrant types apart.** Textual warrant, interpretive bridge and institutional
  warrant stay separate (README's opening); a count, an imported source, a checksum or an
  automated extraction adds no reading credit and supplies no new scholarly acceptance. A
  result that quietly pools them is a different claim than the one this paper makes.
- **A run is bound to its inputs and writes to a new destination.** `publication*.py`,
  `review_timing_run.py`, `review_comparison_run.py` and `review_pressure_run.py` each bind an
  epoch to its pinned inputs, publish exclusively, and write the completion receipt last.
  Re-running is a new epoch, never an overwrite — [maintenance](../docs/maintenance.md) owns
  custody.
- **Historical producers stay attached to their bytes.** The current 1.0.0 software selects a
  specific Blake pin and the retired statistics re-export is gone, while the published
  qualification remains attached to its original source
  (`research/methods-retirement-20261103.json`). Do not reconcile the two by editing a record.
- **Admission and rendering are separate jobs.** The `publication*` and `manuscript.py` modules
  verify references and selected quotations before any render; the actual pinned writers run
  in `tools/template_render.py`. Read the [native guide](../docs/manuscript/README.md) before
  moving that line.
- **The CLI is the entry point.** `pyproject.toml` declares `blakean = "blakean_federalism.cli:app"`.
  Run `blakean --help` for the current command set rather than trusting a list in prose.
- **Lint, types and coverage are gates.** The block in [README.md](../README.md) covers
  `basedpyright`, `ruff check`, `ruff format --check` and separate application and tool
  coverage reports. Copy it rather than reconstructing it.

## What this directory does not have

No CI that exercises it: `.github/` holds `dependabot.yml` only, so this suite runs only when
a person or a lane runs it. No coverage floor in `pyproject.toml` — the floors are arguments
in the verification commands in [README.md](../README.md), and they are two, not one.
