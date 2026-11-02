#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ─── How to run ───
# 1. Install uv: https://docs.astral.sh/uv/
# 2. In the qualified project: uv run --locked python -m tools.audit_review_timing
# 3. Supply --root and a fresh --output below that root's analysis_output directory.
# ──────────────────
# Copyright (c) 2026 Daniel Ari Friedman
"""Run the fixed, source-bound timing atlas through a real private application CLI."""

from __future__ import annotations

from blakean_federalism.review_timing_cli import app

if __name__ == "__main__":
    app()
