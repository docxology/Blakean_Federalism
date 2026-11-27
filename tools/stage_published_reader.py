"""Stage an admitted published edition for a standalone Template reader build."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypedDict, cast
from zipfile import ZipFile

IMAGE = re.compile(
    r"^!\[(?P<alt>.+)\]\(\.\./figures/(?P<file>[^/)]+)\)\{#(?P<label>fig:[^ }]+)", re.M
)
NUMBER = re.compile(
    r"(?<![A-Za-z0-9_@.-])-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?!(?:[A-Za-z0-9_-]|\.\d))"
)


class Asset(TypedDict):
    sha256: str
    bytes: int


class Release(TypedDict):
    release_tag: str
    assets: dict[str, Asset]


class Arguments(argparse.Namespace):
    archive: Path = Path()
    archive_sha256: str = ""


PARTS = {
    "00_graphical_abstracts.md": "00_graphical_abstracts.md",
    "01_notation.md": "01_notation.md",
    "states-change.md": "02_states-change.md",
    "references-and-rights.md": "90_references-and-rights.md",
    "90_atlas.md": "91_atlas.md",
}
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
FORMALISM = re.compile(r"^:{3,}\s+\{\.[\w-]+\s+#((?:def|prop|thm|lem|cor|rem|ax|ex):[\w-]+)\b", re.M)


def retained_text(source: str, rendered: str) -> str:
    """Resolve placeholders using corresponding lines of the published combined input."""
    result = []
    for line in source.splitlines(keepends=True):
        match = TOKEN.search(line)
        if match:
            suffix = line[match.end():].removesuffix("\n")
            pattern = "^" + re.escape(line[:match.start()]) + "(.+?)" + re.escape(suffix) + "$"
            candidates = re.findall(pattern, rendered, flags=re.M)
            if len(candidates) != 1:
                raise ValueError(f"Ambiguous or missing published value: {match[1]}")
            line = line[:match.start()] + candidates[0] + line[match.end():]
            if TOKEN.search(line):
                raise ValueError(f"Unresolved published value on line containing {match[1]}")
        result.append(line)
    return "".join(result)


def stage(root: Path, archive: Path, digest: str) -> None:
    """Check the public ZIP and stage only the paper inputs in a fresh output tree."""
    release = cast(Release, json.loads((root / "research/publication-20261103.json").read_bytes()))
    filename = "Blakean_Federalism-1.0.0-rendering-inputs.zip"
    record = release["assets"][filename]
    with archive.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != digest or actual != record["sha256"] or archive.stat().st_size != record["bytes"]:
        raise ValueError("Archive does not match the caller pin and public release receipt")

    output = root / "output"
    if output.exists():
        raise FileExistsError(output)
    with ZipFile(archive) as package, TemporaryDirectory(dir=root) as temporary:
        manifest_name = "BUNDLE-MANIFEST.json"
        manifest = cast("dict[str, str]", json.loads(package.read(manifest_name)))
        if sorted(package.namelist()) != sorted([*manifest, manifest_name]):
            raise ValueError("ZIP members differ from manifest")
        for member, expected in manifest.items():
            if hashlib.sha256(package.read(member)).hexdigest() != expected:
                raise ValueError(f"ZIP member differs from manifest: {member}")

        staged = Path(temporary) / "output"
        manuscript = staged / "manuscript"
        figures = staged / "figures"
        data = staged / "data"
        manuscript.mkdir(parents=True)
        figures.mkdir()
        data.mkdir()
        rendered = package.read("paper/output/web/_combined_manuscript.md").decode()
        registry: list[dict[str, str]] = []
        formalism_claims: list[dict[str, str]] = []
        for source, display in PARTS.items():
            original = package.read(f"paper/manuscript/{source}").decode()
            text = retained_text(original, rendered)
            (manuscript / display).write_text(text, encoding="utf-8")
            for label in FORMALISM.findall(text):
                formalism_claims.append({
                    "claim_id": f"retained-formalism-{label}",
                    "kind": "citation",
                    "value": label,
                    "artifact_path": f"output/manuscript/{display}",
                })
            for match in IMAGE.finditer(text):
                image = match["file"]
                (figures / image).write_bytes(package.read(f"paper/output/figures/{image}"))
                registry.append({"label": match["label"], "filename": image, "alt_text": match["alt"]})
        for name in ("preamble.md", "references.bib"):
            (manuscript / name).write_bytes(package.read(f"paper/manuscript/{name}"))
        config = json.loads(package.read("paper/manuscript/config.yaml"))
        cover = Path(config["paper"]["cover"]["image"]).name
        (figures / cover).write_bytes(package.read(f"paper/output/figures/{cover}"))
        config["paper"]["description"] = "Reader build from checksum-verified public v1.0.0 rendering inputs."
        config["publication"].update(
            release_status="Reader build of the published 1.0.0 edition",
            repository_label="Public research repository",
            doi_status="Published edition identifier",
        )
        (manuscript / "config.yaml").write_text(
            "# Generated manuscript ordering\n" + json.dumps(config, indent=2) + "\n", encoding="utf-8"
        )
        (figures / "figure_registry.json").write_text(
            json.dumps({"schema_version": 1, "figures": registry}, indent=2) + "\n", encoding="utf-8"
        )
        # Quantities attest to parity with the deposited text, not new measurements.
        with (data / "retained-reader-values.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("value", "source"))
            for name in PARTS.values():
                text = (manuscript / name).read_text(encoding="utf-8")
                values = sorted({match[0] for match in NUMBER.finditer(text)})
                writer.writerows((value, name) for value in values)
        (data / "formalism-claim-ledger.json").write_text(
            json.dumps({"claims": formalism_claims}, indent=2) + "\n", encoding="utf-8"
        )
        staged.rename(output)
    print(f"Verified {len(manifest)} bundle members.")
    print(f"Staged {len(registry)} figures plus the cover.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("--archive", type=Path, required=True)
    _ = parser.add_argument("--archive-sha256", required=True)
    args = parser.parse_args(namespace=Arguments())
    stage(Path(__file__).resolve().parents[1], args.archive, args.archive_sha256)
