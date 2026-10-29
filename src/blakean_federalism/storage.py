# Copyright (c) 2026 Daniel Ari Friedman
"""Compatibility imports for shared Blake custody; no private storage engine."""

from blake.methods.storage import (
    copy_new,
    digest,
    publish_projection,
    safe_path,
    verify_file,
    write_new,
)

__all__ = ["copy_new", "digest", "publish_projection", "safe_path", "verify_file", "write_new"]
