"""Verify the local publication identity and rasterize the tracked overview."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent
ROOT = FIXTURE.parents[2]
ARTICLE = ROOT / "Blakean_Federalism.pdf"
OVERVIEW = ROOT / "docs/assets/overview.svg"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="New disposable project named Blakean_Federalism")
    project = parser.parse_args().project.resolve()
    if project.name != "Blakean_Federalism" or project.exists():
        parser.error("project must name a fresh directory called Blakean_Federalism")

    record = json.loads((ROOT / "publication.json").read_text(encoding="utf-8"))["pdf"]
    with ARTICLE.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    info = subprocess.check_output(["pdfinfo", str(ARTICLE)], text=True, env={**os.environ, "LC_ALL": "C"})
    pages = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if (
        digest != record["sha256"]
        or ARTICLE.stat().st_size != record["bytes"]
        or pages is None
        or int(pages[1]) != record["pages"]
    ):
        raise SystemExit("The local PDF disagrees with the recorded publication identity.")

    shutil.copytree(FIXTURE / "note-source", project / "docs/manuscript")
    subprocess.run(["git", "init", "--quiet", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "add", "--", "docs/manuscript"], check=True)

    figures = project / "output/figures"
    figures.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["inkscape", "--export-text-to-path", str(OVERVIEW), f"--export-filename={figures / 'overview.png'}"],
        check=True,
    )
    entry = {
        "label": "fig:overview",
        "filename": "overview.png",
        "caption": "Explanatory overview of the published working paper.",
        "generated_by": "docs/assets/overview.svg",
        "metadata": {
            "alt_text": (
                "The States Change overview connects corpus evidence, formal distinctions, "
                "hypothetical cases and person-specific review to the argument about shared rule."
            ),
        },
    }
    (figures / "figure_registry.json").write_text(
        json.dumps({entry["label"]: entry}, indent=2) + "\n", encoding="utf-8"
    )
    reports = project / "output/reports"
    reports.mkdir(parents=True, exist_ok=True)
    receipt = {
        "published_pdf": record,
        "publication_record_sha256": hashlib.sha256((ROOT / "publication.json").read_bytes()).hexdigest(),
        "source_overview_sha256": hashlib.sha256(OVERVIEW.read_bytes()).hexdigest(),
        "render_overview_sha256": hashlib.sha256((figures / "overview.png").read_bytes()).hexdigest(),
    }
    (reports / "local-edition.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Verified {record['pages']} pages, {record['bytes']} bytes and SHA-256 {digest}")


if __name__ == "__main__":
    main()
