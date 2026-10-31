# Copyright (c) 2026 Daniel Ari Friedman
"""Drive the registered planning commands through real local subprocesses."""

import json
import subprocess
import sys
from typing import Final

import pytest
from blake.methods.runs import digest

from .test_review_planning import (
    PlanningFixture,
    authored_file,
    bind_request,
    original_review_run,
    request_for,
)
from .test_review_planning import (
    planning as planning_source,
)

# Export the reused real pytest fixture for module-level discovery.
__all__ = ["original_review_run", "planning_source"]


CLI_MODULE: Final = "blakean_federalism.cli"


def run_cli(fixture: PlanningFixture, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 -- fixed interpreter/module, real isolated CLI controls
        [sys.executable, "-m", CLI_MODULE, *arguments],
        cwd=fixture.root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )


def test_real_cli_publishes_and_verifies_independently_pinned_pairs(planning_source) -> None:
    # Given one pinned original run and request in a private fixture root.
    source = bind_request(planning_source, request_for(planning_source))
    output = planning_source.root / "analysis_output/cli-batch"
    arguments = ["--request", str(source.path), "--request-sha256", source.sha256]
    # When the registered plan command publishes a real batch.
    result = run_cli(planning_source, ["plan-review", *arguments, "--output", str(output)])
    # Then the result binds the original run/request and has no authored decisions.
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    assert receipt["source_run_sha256"] == planning_source.sha256
    assert receipt["source_context_sha256"] == source.sha256
    assert not (output / "decisions.jsonl").exists()
    batch_sha = digest((output / "run.json").read_bytes())
    verified = run_cli(
        planning_source,
        ["verify-review", *arguments, "--batch", str(output), "--batch-sha256", batch_sha],
    )
    assert verified.returncode == 0, verified.stderr
    assert json.loads(verified.stdout)["spec"]["source_context_sha256"] == source.sha256


@pytest.mark.parametrize("failure", ["request-pin", "schema", "decisions-pin", "source-run-pin"])
def test_real_cli_refuses_untrusted_request_before_output(planning_source, failure) -> None:
    # Given a request whose deliberate fault still crosses the actual JSON/CLI boundary.
    request = request_for(planning_source)
    source = bind_request(planning_source, request)
    payload = json.loads(source.path.read_text())
    match failure:
        case "request-pin":
            expected = "0" * 64
        case "schema":
            payload["selection"]["target_size"] = True
            expected = ""
        case "decisions-pin":
            decisions = authored_file(planning_source, (planning_source.hits[0],))
            payload["decisions"] = {"path": str(decisions.path), "sha256": "0" * 64}
            expected = ""
        case "source-run-pin":
            payload["source_run_sha256"] = "0" * 64
            expected = ""
    if not expected:
        source.path.write_text(json.dumps(payload) + "\n")
        expected = digest(source.path.read_bytes())
    output = planning_source.root / "analysis_output/cli-refused"
    # When the real registered CLI sees that fault.
    result = run_cli(
        planning_source,
        [
            "plan-review",
            "--request",
            str(source.path),
            "--request-sha256",
            expected,
            "--output",
            str(output),
        ],
    )
    # Then it fails and publishes no incomplete/complete batch.
    assert result.returncode != 0
    assert result.stderr
    assert not output.exists()


def test_real_cli_wrong_batch_pin_cannot_verify(planning_source) -> None:
    # Given a correctly published batch and independently held request.
    source = bind_request(planning_source, request_for(planning_source))
    output = planning_source.root / "analysis_output/cli-batch"
    arguments = ["--request", str(source.path), "--request-sha256", source.sha256]
    made = run_cli(planning_source, ["plan-review", *arguments, "--output", str(output)])
    assert made.returncode == 0, made.stderr
    original = (output / "run.json").read_bytes()
    # When verification supplies a false completion-receipt pin.
    result = run_cli(
        planning_source,
        ["verify-review", *arguments, "--batch", str(output), "--batch-sha256", "0" * 64],
    )
    # Then verification fails without modifying the published batch.
    assert result.returncode != 0
    assert (output / "run.json").read_bytes() == original


def test_registered_existing_commands_remain_available(planning_source) -> None:
    # Given the real full application CLI after planning registration.
    # When its command help is requested.
    result = run_cli(planning_source, ["--help"])
    # Then the actual command interface still exposes prior retrieval/review commands.
    assert result.returncode == 0, result.stderr
    for command in (
        "analyze",
        "search-corpus",
        "search-study",
        "corpus-statistics",
        "prepare-evidence-review",
        "plan-review",
        "verify-review",
    ):
        assert command in result.stdout
