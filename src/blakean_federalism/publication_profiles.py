# Copyright (c) 2026 Daniel Ari Friedman
"""Explicit private edition policies; historical selections remain reproducible."""

from typing import Final

ILLUMINATED_EDITIONS: Final = frozenset(
    {"0.11.0", "0.12.0", "0.13.0", "0.14.0", "0.15.0", "0.16.0", "0.17.0", "0.18.0", "0.19.0"}
)
AUTHORITY_PRODUCERS: Final = ILLUMINATED_EDITIONS - {"0.11.0"}
ANALYTICAL_PRODUCERS: Final = AUTHORITY_PRODUCERS - {"0.12.0", "0.13.0"}
