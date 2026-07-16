# Release Plan

## Current Decision

Status: `BLOCKED — CHARTER, SECURITY, PROVENANCE, AND APPROVAL EVIDENCE REQUIRED`

No release is ready. The repository now contains a product directive and changelog entry for a documentation-only Alistaire charter, but `punchlist.md` is absent, P0 remains `READY`, candidate head `867c55a5b717eb3426f43c13638c7420a9cb6951` has no commit-status checks or workflow runs, and no complete charter, deterministic validation, security/privacy review, documentation verification, provenance bundle, or approval record exists.

## Versioning

- Scheme: Semantic Versioning.
- First eligible candidate: `0.0.1-charter`.
- The `charter` prerelease label denotes documentation and contract proposals only; it must not imply an executable AGI, consciousness, sentience, autonomous learning, or production system.
- Any executable candidate requires a later version after the charter is approved and upstream QSO contracts are pinned and verified.
- Tag only an immutable commit satisfying every gate included below.

## Release Scope

The first candidate is documentation-only and may include:

- approved product purpose, intended users, use cases, non-goals, terminology, and prohibited claims;
- authoritative QSO subsystem composition and repository ownership map;
- proposed versioned contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, and `Bridge`;
- lifecycle, inter-QSO communication, conflict resolution, uncertainty, evidence, freeze, shutdown, rollback, and human-approval flows;
- bounded-learning policy covering allowed sources, persistence, privacy, time, resource, size, and network limits;
- threat model, credential boundary, external-tool restrictions, and misuse/abuse analysis;
- deterministic evaluation and adversarial-fixture specification for identity consistency, memory integrity, policy compliance, recovery, and bounded adaptation;
- GitHub Pages documentation map, onboarding, limitations, provenance, and review instructions.

Runtime code, external data ingestion, persistent learning, autonomous tool use, deployment, and production capability claims are outside this candidate.

## Selected Completed Work

The following completed work is eligible to be incorporated into the eventual charter candidate, but is not independently releasable:

- `taskchain.md`: evidence-bounded product directive, documentation-only MVP boundary, dependency sequence, approval gates, roadmap, builder rules, and evidence rules.
- `changelog.md`: recorded product decision, non-claims, sequencing, and current evidence state.

No task is `DONE`; no completed charter artifact or release evidence bundle is currently selected for tagging.

## Planned Changelog Entries

- `Added`: approved Alistaire product and architecture charter.
- `Added`: QSO composition, lifecycle, trust-boundary, evidence-flow, freeze, shutdown, and rollback diagrams.
- `Contracts`: versioned inter-repository dependency and ownership matrix.
- `Security`: privacy, credential, learning-source, external-tool, prompt/data injection, persistence, and misuse threat-model findings.
- `Testing`: deterministic charter validation, link/schema checks, dependency consistency checks, and adversarial evaluation specifications.
- `Documentation`: onboarding, terminology, limitations, prohibited claims, operating assumptions, and Pages map.
- `Release`: source archive, checksums, provenance manifest, gate results, and approval record for `0.0.1-charter`.

## Acceptance Gates

| Gate | Status | Requirement |
|---|---|---|
| Task completion | FAIL | P0 charter work is decomposed in `punchlist.md`, completed, evidenced, and marked `DONE`. |
| Charter completeness | FAIL | Purpose, users, use cases, non-goals, QSO responsibilities, inputs/outputs/state/failures, lifecycle, and ownership are approved. |
| Dependency contracts | NO EVIDENCE | Upstream repositories and candidate versions are identified; ownership does not overlap; unresolved contracts are explicitly blocked rather than guessed. |
| Tests and validation | NO EVIDENCE | Markdown/link/schema checks, terminology consistency, diagrams, dependency matrix, deterministic evaluation plan, and negative/adversarial fixtures pass reproducibly. |
| Security and privacy | NO EVIDENCE | Secret scan and documented review cover credentials, private data, learning sources, persistence, network/tool authority, injection, exfiltration, self-modification, and shutdown bypass. |
| Documentation | PARTIAL | Product directive exists; complete charter, architecture, Pages map, onboarding, limitations, and review instructions are absent or unverified. |
| Provenance | NO EVIDENCE | Commit, dependency refs, tool versions, commands, timestamps, outputs, artifact hashes, repository URL, reviewers, and attestations are retained. |
| Rollback and shutdown | NO EVIDENCE | Freeze, stop, restore, data-retention, and failed-candidate withdrawal procedures are explicit and reviewable. |
| Repository-specific acceptance | FAIL | The charter distinguishes implemented, planned, hypothetical, and prohibited claims and resolves every approval gate in `taskchain.md`. |
| Approval | PENDING | Explicit approval is recorded only after all blocking gates pass. |

## Artifact Requirements

- Approved product/architecture charter in Markdown.
- QSO subsystem responsibility and ownership matrix.
- Versioned dependency/contract manifest with immutable commit or tag references where available.
- Architecture, data/control flow, trust-boundary, evidence-flow, freeze/shutdown, and rollback diagrams.
- Security/privacy threat model and review report.
- Deterministic evaluation plan and adversarial-fixture specification.
- Documentation validation outputs, link/schema reports, and limitations/non-claims statement.
- Machine-readable release gate report where practical.
- Source archive, SHA-256 checksum manifest, and provenance/attestation manifest.
- Approval record identifying the reviewed candidate commit.

## Rollback Criteria

Withdraw or roll back the candidate if documentation validation is non-reproducible, dependency ownership conflicts remain, contracts reference mutable or unavailable interfaces without qualification, security/privacy boundaries are incomplete, learning or tool authority exceeds the approved charter, freeze/shutdown behavior is ambiguous, capability claims exceed evidence, approval records are missing, or artifact hashes differ. Remove or invalidate the candidate tag/release, restore the last reviewed commit, retain failed-candidate evidence, and do not begin runtime implementation from an unapproved charter.

## Unresolved Blockers

- `punchlist.md` and a repository-health evidence log are absent.
- P0 remains `READY`; the product/architecture charter has not been produced or approved.
- Candidate head has no commit-status checks or workflow runs.
- No current tests, security/privacy review, documentation verification, provenance, checksums, or rollback evidence exists.
- Upstream QSO contract versions are not pinned or accepted for this repository.
- Runtime work remains blocked behind QSO-GENOMES and QuantumStateObjects baselines.
- Approval is required for product identity: research agent framework, interactive companion, or both.
- Approval is required for the authoritative QSO subsystem list and repository ownership boundaries.
- Approval is required for allowed learning sources, persistence model, and privacy policy.
- Approval is required for freeze, shutdown, rollback, and human-approval behavior.
- Approval is required for whether the first executable MVP is local-only, simulation-only, or includes a user interface.

## Release Log

- 2026-07-16: Established the documentation-only `0.0.1-charter` candidate and comprehensive release gates; release remains blocked pending charter completion, repository health evidence, security/privacy validation, provenance, rollback evidence, and explicit approvals.
