# Copyright (c) 2026 Daniel Ari Friedman
"""Run the pinned template's actual hydration, PDF and HTML writers."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main() -> None:  # noqa: PLR0912, PLR0915 -- Visible source/call/custody transaction.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    stage = args.stage.absolute()
    template = args.template_root.absolute()
    prepared = json.loads((stage / "prepared-publication.json").read_text())
    expected = prepared["template"]["commit"]
    os.environ["SOURCE_DATE_EPOCH"] = str(prepared["template"]["source_date_epoch"])
    os.environ["FORCE_SOURCE_DATE"] = "1"
    os.environ["TZ"] = "UTC"
    git = shutil.which("git")
    if git is None:
        raise ValueError("git_missing")
    actual = subprocess.check_output(  # noqa: S603 -- Resolved Git and fixed read-only argv.
        [git, "-c", "core.fsmonitor=false", "-C", str(template), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != expected:
        raise ValueError("template_pin")
    dirty = subprocess.check_output(  # noqa: S603 -- Resolved Git and fixed read-only argv.
        [
            git,
            "-c",
            "core.fsmonitor=false",
            "-C",
            str(template),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ]
    )
    if dirty:
        raise ValueError("template_dirty")
    if any(Path(x).stat().st_dev != stage.stat().st_dev for x in (sys.prefix, sys.base_prefix)):
        raise ValueError("template_runtime_storage")
    index = (
        subprocess.check_output(  # noqa: S603 -- Resolved Git and fixed read-only argv.
            [
                git,
                "-c",
                "core.fsmonitor=false",
                "-C",
                str(template),
                "ls-files",
                "--stage",
                "-z",
                "infrastructure",
                "pyproject.toml",
                "uv.lock",
            ],
            text=True,
        )
        .strip("\0")
        .split("\0")
    )
    gitlinks = {}
    names = []
    for entry in index:
        identity, name = entry.split("\t", 1)
        mode, oid, _ = identity.split()
        if mode == "160000":
            gitlinks[name] = oid
        elif mode in {"100644", "100755"}:
            names.append(name)
        else:
            raise ValueError("unsupported_template_source_mode")
    before = {name: file_hash(template / name) for name in names}
    sys.path.insert(0, str(template))
    import infrastructure.rendering
    from infrastructure.rendering import RenderingConfig
    from infrastructure.rendering.manuscript_injection import (
        substitute_manuscript_text,
        write_resolved_manuscript_tree,
    )
    from infrastructure.rendering.pdf_renderer import PDFRenderer
    from infrastructure.rendering.web_renderer import WebRenderer

    if not Path(infrastructure.rendering.__file__).is_relative_to(template):
        raise ValueError("template_import_origin")
    variables = json.loads((stage / "manuscript_variables.json").read_text())
    for path in (stage / "manuscript").iterdir():
        if path.suffix in (".md", ".yaml"):
            _, missing = substitute_manuscript_text(path.read_text(), variables)
            if missing:
                raise ValueError(", ".join(missing))
    manuscript = write_resolved_manuscript_tree(stage, variables)
    sources = [manuscript / name for name in prepared["source_order"]]
    config = RenderingConfig(
        manuscript_dir=str(manuscript),
        figures_dir=str(stage / "output/figures"),
        output_dir=str(stage / "output"),
        pdf_dir=str(stage / "output/pdf"),
        web_dir=str(stage / "output/web"),
        enable_slides=False,
    )
    pdf = PDFRenderer(config).render_combined(
        sources, manuscript, project_name="blakean_federalism"
    )
    html = WebRenderer(config).render_combined(
        sources, manuscript, project_name="blakean_federalism"
    )
    after = {name: file_hash(template / name) for name in names}
    if before != after:
        raise ValueError("template_source_changed")
    record = {
        "template_repository": prepared["template"]["repository"],
        "template_commit": actual,
        "template_sources": before,
        "template_gitlinks": gitlinks,
        "template_sources_unchanged": True,
        "runtime": {"prefix": sys.prefix, "base_prefix": sys.base_prefix, "version": sys.version},
        "pdf": pdf.relative_to(stage).as_posix(),
        "html": html.relative_to(stage).as_posix(),
        "outputs": {
            pdf.relative_to(stage).as_posix(): file_hash(pdf),
            html.relative_to(stage).as_posix(): file_hash(html),
        },
        "resolved_inputs": {
            path.relative_to(stage).as_posix(): file_hash(path)
            for path in manuscript.iterdir()
            if path.is_file()
        },
        "writer_calls": prepared["template"]["writers"],
        "scope": (
            "Actual native template execution; rendered verification and "
            "independent review are separate"
        ),
    }
    with (stage / "native-render-receipt.json").open("x") as stream:
        stream.write(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"pdf": record["pdf"], "html": record["html"], "template_commit": actual}))


if __name__ == "__main__":
    main()
