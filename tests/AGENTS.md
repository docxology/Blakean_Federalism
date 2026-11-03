# AGENTS.md — `tests/`

**Audience:** agents adding or changing tests.

One module per area — abstract analysis and the illuminated abstracts, corpus and research
workbench, institutional review and its experiments, the three review studies
(`test_review_planning*`, `test_review_comparison*`, `test_review_pressure*`,
`test_review_timing*`), search, publication and native output, and the CLI modules that drive
the real commands. `pyproject.toml` collects `tests` only; `conftest.py` and `tests/__init__.py`
are shared ground, so build on them rather than around them.

## Rules

- **Two profiles, and they are not the same gate.** [README.md](../README.md)'s *Run locally*
  block is the bounded source-only profile; its *Verification* block is the full gate and
  **requires the retained research fixtures**. Missing-fixture errors are not a pass, and a
  source-only run does not clear the full gate.
- **Read both floors.** The verification block reports the application and the `tools`
  directory separately (`--fail-under 90` and `--fail-under 60`), and the root guide is
  explicit that a combined headline does not establish both. The floors live in those commands.
- **Real files, real CLI, real refusal.** The root guide's rule: exercise the actual command
  with a positive case *and* its rejecting control. A test that only proves the happy path is
  the thing that reads as coverage while proving nothing.
- **Some tests exercise `tools/` directly** — `test_manuscript.py` and
  `test_institutional_review_tool.py` — so a tool change can break the suite while the package
  is untouched.
- **Do not pool people or scores in a test's expectations.** The application deliberately
  reports person-specific requirements and conditions without a scalar ranking; a test that
  asserts a combined score is asserting a claim the repository refuses to make.
- **A documentation edit is not a test edit.** The root guide is explicit that documentation
  needs link, command and evidence-claim review rather than a test that pins prose.

## What is absent here

No CI: `.github/` holds `dependabot.yml` only, so nothing runs this suite unless a person or a
lane does, and a green run is evidence of that run and no other.
