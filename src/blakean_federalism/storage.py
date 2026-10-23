# Copyright (c) 2026 Daniel Ari Friedman
"""Regular-file custody and complete-file publication for private derived data."""

import hashlib
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath

from .models import FileReceipt, ResearchError


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


def copy_new(source: Path, destination: Path) -> None:
    """Copy into a new exclusive file; preserve any occupied destination."""
    try:
        with source.open("rb") as incoming, destination.open("xb") as outgoing:
            shutil.copyfileobj(incoming, outgoing)
            outgoing.flush()
            os.fsync(outgoing.fileno())
    except FileExistsError as exc:
        raise ResearchError("occupied_output", str(destination)) from exc


def publish_projection(
    stage: Path,
    destination: Path,
    files: tuple[FileReceipt, ...],
    receipt_json: str,
) -> None:
    """Reserve a new directory atomically; publish the reader's completion marker last."""
    for entry in files:
        _ = verify_file(stage, entry.path, entry.size, entry.sha256)
    try:
        destination.mkdir()
    except FileExistsError as exc:
        raise ResearchError("occupied_output", str(destination)) from exc
    for entry in files:
        copy_new(stage / entry.path, destination / entry.path)
        _ = verify_file(destination, entry.path, entry.size, entry.sha256)
    # A failed partial destination is retained and has no valid completion marker.
    write_new(destination / "import-receipt.json", receipt_json)
