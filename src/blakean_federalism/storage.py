# Copyright (c) 2026 Daniel Ari Friedman
"""Regular-file custody and complete-file publication for private derived data."""

import hashlib
import os
import tempfile
from pathlib import Path, PurePosixPath

from .models import ResearchError


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Reject symlinks, traversal and nonregular inputs before reading bytes."""
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or "\\" in relative:
        raise ResearchError("unsafe_path", relative)
    if any(part.is_symlink() for part in (root, *root.parents)):
        raise ResearchError("symlink_root", str(root))
    path = root.joinpath(*rel.parts)
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ResearchError("symlink_input", relative)
    if not path.is_file():
        raise ResearchError("missing_regular_file", relative)
    return path


def verify_file(root: Path, relative: str, size: int, expected: str) -> Path:
    path = safe_path(root, relative)
    if path.stat().st_size != size or digest(path) != expected:
        raise ResearchError("checksum_mismatch", relative)
    return path


def write_new(path: Path, content: str) -> None:
    """Publish a new complete file without replacing another run or following symlinks."""
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ResearchError("symlink_output", str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent) as stream:
        _ = stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        try:
            os.link(stream.name, path)
        except FileExistsError as exc:
            raise ResearchError("occupied_output", str(path)) from exc
