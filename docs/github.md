# GitHub, citation and dependency maintenance

The public [Blakean Federalism repository](https://github.com/docxology/Blakean_Federalism) hosts
the maintained application and authored research. Its homepage resolves to
[the published 1.0.0 working paper](https://doi.org/10.5281/zenodo.23900617).
Use [CITATION.cff](../CITATION.cff) for the preferred paper citation,
[the PDF](../Blakean_Federalism.pdf) for the deposited edition, and
[publication facts](../publication.json) for exact release identities.
The [GitHub release](https://github.com/docxology/Blakean_Federalism/releases/tag/v1.0.0)
contains eight assets: software, frozen rendering inputs, source map,
checksums, PDF and third-party font notices.

Later main commits maintain instructions and tools. They do not silently
change the release tag, deposited PDF, original analytical producer or software
version. The [dated GitHub maintenance record](../research/github-maintenance-20261103.json)
binds this follow-up; the preceding documentation record retains its own epoch.

## Entry points and ownership

Start with [the README](../README.md), [project status](PROJECT_STATUS.md),
[agent instructions](../AGENTS.md), [authoring style](style-guide.md) and
[the actual template workflow](manuscript/README.md). Public
[Blake](https://github.com/docxology/blake) owns reusable corpus custody and
methods. This application owns its question, selections, domain policy,
interpretations and manuscript; the sibling application is independent.

The repository description, homepage and topics describe that scope. The
[distribution terms](../LICENSE-PAPER.md) and [privacy contract](../PRIVACY.md)
govern authored and third-party material. Public visibility does not relicense
the application or restricted inputs. GitHub's “Other” license label reflects
the reserved research license.

## Reviews and hosted checks

Main is protected and integration uses pull requests. Current protection
enforces that route for administrators; its required GitHub approval count is
zero. Preserve separately required source review, real local checks and
publication authority. An empty GitHub review list is not independent review.

GitGuardian checks secrets. It does not execute the Python suite, inspect every
PDF page, adjudicate readings or certify accessibility. No repository Actions
workflow currently runs those research gates. Use the explicit source-only
and retained-fixture profiles in the README; missing private data is not a pass.
Enabling Actions in settings does not itself run a workflow.

Keep unresolved research in project status; use public issues for concrete
source defects. Provider bodies, full concordances, scholarly PDFs, credentials,
private indexes and recovery evidence remain outside GitHub custody.

## Maintained and historical dependency files

[Dependabot configuration](../.github/dependabot.yml) uses the actual uv
ecosystem. The root environment remains eligible for automated security-update
PRs. Scheduled version-update PRs are disabled with open-pull-requests-limit
set to zero; security updates have their own behavior.

Each exact archived manifest directory is listed separately with an all-package
ignore rule. This prevents update PRs from rewriting historical producer locks.
It does not dismiss their alerts, patch those old environments, or make them
current installation targets. Historical execution needs its own bounded
dependency/runtime qualification. When retaining another environment, add its
exact manifest directory to this policy and record the new epoch.

This uses dependency ignore rules because exclude-paths is documented for
version updates only. See GitHub's [dependency-update controls](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/controlling-dependencies-updated)
and [option reference](https://github.com/github/docs/blob/main/content/code-security/reference/supply-chain-security/dependabot-options-reference.md).
A historical-lock-only PR should be closed after preserving its exact tip.
Maintained-root fixes receive current installed qualification and ordinary review.
Actual hosted ingestion and future PR behavior remain separate from local
configuration validation.

## Branch and worktree custody

Completed branches are retired after exact-tip preservation. Recovery refs and
verified bundles remain on GitVault. The [maintenance guide](maintenance.md)
records the supported refusal to remove protected shared-store and locked
worktrees. Preserve their heads, ignored fixtures, environments and original
review records; GitHub housekeeping authorizes no manual deletion or unlocking.
