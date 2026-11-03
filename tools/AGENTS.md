# AGENTS.md — `tools/`

**Audience:** agents changing the standalone production scripts.

`tools/` is a Python package (`__init__.py`) holding four source-bound scripts: the two audits
(`audit_institutional_review.py` over admissible baseline decisions, `audit_review_timing.py`
through the real private application CLI), `acquire_manuscript.py`, which recovers only the
explicitly selected manuscript inputs into ignored storage, and `template_render.py`, which
runs the pinned template's actual hydration, PDF and HTML writers.

The repository contract is [the root guide](../AGENTS.md); the reader's view is
[README.md](../README.md), whose *Verification* block reports this directory's coverage
separately with its own floor.

## Rules

- **Acquisition is explicit and lands in ignored storage.** `acquire_manuscript.py` recovers
  the selected inputs and nothing else; a tool never widens what it fetches, and no acquired
  source or provider expression is written into a tracked path
  ([privacy and custody](../PRIVACY.md)).
- **Audits are hash-bound to admissible inputs.** The institutional audit runs against
  hash-bound baseline decisions rather than whatever is on disk; adding an input means pinning
  it, not defaulting it.
- **Runs publish exclusively and receipt last.** A tool writes a new epoch to an unused
  destination and closes it with a completion receipt; retained failures and producers stay
  intact ([maintenance](../docs/maintenance.md)).
- **The import direction is one-way.** Nothing under `src/` imports `tools/`;
  `tests/test_manuscript.py` and `tests/test_institutional_review_tool.py` do. A tool may use
  the package; the package may not reach back into `tools/`.
- **`template_render.py` is the rendering boundary.** It runs the pinned template's writers and
  therefore changes published bytes: a change here needs the
  [native guide](../docs/manuscript/README.md)'s qualification and complete-page acceptance,
  not only a green suite.
