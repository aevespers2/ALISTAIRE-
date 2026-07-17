# Release Plan

## Current decision

Status: `BLOCKED — CANONICAL REPOSITORY, CHARTER, SECURITY, PROVENANCE, AND APPROVAL REQUIRED`

No release is ready. `aevespers2/ALISTAIRE-` contains the established product directive, while the newly created `aevespers2/Alistaire-agi` presents the same Alistaire/QSO product identity and a broad placeholder documentation tree. P0 is therefore blocked on selection of one canonical repository and an approved migration/redirect/archive plan before charter completion or runtime work. No executable AGI, autonomous-learning, deployment, test, security, provenance, or release capability is established in either repository.

## Versioning

- Scheme: Semantic Versioning after canonical repository selection.
- First eligible candidate: `0.0.1-charter` in the approved canonical repository.
- The `charter` label denotes documentation and contract proposals only; it must not imply executable AGI, consciousness, sentience, autonomous learning, or production readiness.
- The non-canonical repository must not publish a competing package or release identity.
- Any executable candidate requires a later version after the charter and upstream QSO contracts are approved and verified.

## Candidate scope

The first candidate is documentation-only and may include:

- canonical repository, package/display name, migration map, redirects/archive notice, and preserved provenance;
- approved product purpose, intended users, product mode, use cases, non-goals, terminology, and prohibited claims;
- authoritative QSO subsystem composition and repository ownership map;
- proposed versioned contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, and `Bridge`;
- lifecycle, communication, conflict resolution, uncertainty, evidence, freeze, shutdown, rollback, and human-approval flows;
- bounded-learning policy covering allowed sources, persistence, privacy, time, resource, size, and network limits;
- threat model, credential boundary, external-tool restrictions, and misuse/abuse analysis;
- deterministic evaluation and adversarial-fixture specification;
- one consolidated GitHub Pages documentation map, onboarding, limitations, provenance, and review instructions.

Runtime code, external data ingestion, persistent learning, autonomous tool use, deployment, and production capability claims are outside this candidate.

## Selected completed work

- `taskchain.md` defines the evidence-bounded charter direction and current duplicate-repository hold.
- `punchlist.md` now decomposes canonical-repository selection, charter work, documentation validation, security/privacy review, provenance, artifact, and rollback requirements.
- `changelog.md` records the current product coordination state.
- `Alistaire-agi` contains a README and placeholder documentation path scaffold that must be inventoried during consolidation.

These are coordination and inventory artifacts, not a completed charter or release evidence bundle.

## Acceptance gates

| Gate | Status | Requirement |
|---|---|---|
| Canonical repository | BLOCKED | Select canonical repository/package/name and approve migration, provenance, redirect/archive, and ownership plan. |
| Task completion | FAIL | Complete and evidence every blocking item in `punchlist.md`; mark the corresponding task-chain work `DONE`. |
| Charter completeness | FAIL | Purpose, users, product mode, non-goals, QSO responsibilities, lifecycle, and ownership are approved. |
| Dependency contracts | NO EVIDENCE | Upstream repositories and immutable candidate versions are identified without overlapping ownership. |
| Tests and validation | NO EVIDENCE | Documentation/link/schema/terminology/diagram/dependency checks and evaluation fixtures pass reproducibly. |
| Security and privacy | NO EVIDENCE | Secret scan and review cover credentials, private data, learning, persistence, network/tool authority, injection, exfiltration, self-modification, and shutdown bypass. |
| Documentation | PARTIAL | Directives, a punch list, and placeholder paths exist; a substantive consolidated charter and verified Pages site do not. |
| Provenance | NO EVIDENCE | Both histories, migration map, commits, tools, commands, outputs, artifact hashes, and approval record are retained. |
| Rollback and shutdown | NO EVIDENCE | Freeze, stop, restore, data-retention, failed-candidate withdrawal, and repository-consolidation rollback are explicit. |
| Approval | PENDING | Explicit approval is recorded only after all blocking gates pass. |

## Artifact requirements

- Canonical-repository decision and migration/provenance map.
- Redirect/archive notice for the non-canonical repository.
- Approved product/architecture charter.
- QSO responsibility and ownership matrix.
- Versioned dependency/contract manifest.
- Architecture, trust-boundary, evidence-flow, freeze/shutdown, and rollback diagrams.
- Security/privacy threat model and review report.
- Deterministic evaluation and adversarial-fixture specification.
- Documentation validation outputs and limitations/non-claims statement.
- Source archive, SHA-256 checksum manifest, provenance manifest, and approval record.

## Rollback criteria

Withdraw the candidate if two repositories continue publishing competing identities, migration loses history or attribution, documentation validation is non-reproducible, dependency ownership conflicts remain, security/privacy boundaries are incomplete, learning/tool authority exceeds the charter, freeze/shutdown behavior is ambiguous, capability claims exceed evidence, approvals are missing, or artifact hashes differ. Restore the last reviewed state, retain failed-candidate evidence, and do not begin runtime work from an unapproved charter.

## Unresolved blockers

- Canonical Alistaire repository and package identity are not approved.
- Migration, redirect/archive, and provenance plan are absent.
- The existing `punchlist.md` is entirely incomplete and has no immutable evidence entries.
- No completed charter, tests, security/privacy review, documentation verification, dependency pinning, provenance, checksums, rollback evidence, or approval exists.
- Runtime remains blocked behind QSO-GENOMES and QuantumStateObjects baselines.
- Product mode, QSO ownership, learning/persistence/privacy, freeze/shutdown behavior, and first executable operating mode require approval.

## Release log

- 2026-07-16: Reconciled the newly added punch list; the documentation-only candidate remains blocked with no release promoted.
- 2026-07-16: Added the canonical-repository consolidation gate after creation of overlapping `Alistaire-agi`; no release or runtime work approved.
