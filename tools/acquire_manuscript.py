# Copyright (c) 2026 Daniel Ari Friedman
"Recover only the explicitly selected manuscript inputs into ignored storage."

import argparse
import hashlib
from pathlib import Path
from urllib.parse import urlparse

import requests

from blakean_federalism.manuscript import ManuscriptSpec
from blakean_federalism.models import ResearchError
from blakean_federalism.storage import safe_path, verify_file

HOSTS = frozenset({"blake.lib.asu.edu", "tile.loc.gov", "www.loc.gov"})
PREFIXES = (
    Path("local_data/manuscript/v0.2.0"),
    Path("local_data/manuscript/v0.5.0"),
    Path("local_data/manuscript/v0.6.0"),
    Path("local_data/manuscript/v0.7.0"),
    Path("local_data/manuscript/v0.8.0"),
    Path("local_data/manuscript/v0.9.0"),
)


def check_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in HOSTS or parsed.username:
        raise ResearchError("source_url", url)


def acquire(root: Path) -> int:
    spec = ManuscriptSpec.model_validate_json(
        safe_path(root, "research/manuscript-inputs.json").read_bytes()
    )
    targets = []
    for asset in spec.assets:
        relative = Path(asset.path)
        if (
            not any(relative.is_relative_to(prefix) for prefix in PREFIXES)
            or ".." in relative.parts
        ):
            raise ResearchError("acquisition_boundary", asset.path)
        target = root / relative
        if any(part.is_symlink() for part in (target, *target.parents)):
            raise ResearchError("symlink_output", asset.path)
        check_url(asset.url)
        if target.exists():
            verify_file(root, asset.path, asset.size, asset.sha256)
        targets.append((asset, target))
    # No netrc, credentials or environment-proxy lookup is used.
    session = requests.Session()
    session.trust_env = False
    recovered = 0
    for asset, target in targets:
        if target.exists():
            continue
        with session.get(asset.url, timeout=60, stream=True) as response:
            response.raise_for_status()
            check_url(response.url)
            content = response.raw.read(asset.size + 1, decode_content=True)
        if len(content) != asset.size or hashlib.sha256(content).hexdigest() != asset.sha256:
            raise ResearchError("download_checksum", asset.asset_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(content)
        verify_file(root, asset.path, asset.size, asset.sha256)
        recovered += 1
    return recovered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    recovered = acquire(args.root.absolute())
    print(f"Recovered {recovered} new inputs; all declared assets verified")


if __name__ == "__main__":
    main()
