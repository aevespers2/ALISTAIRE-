# Release Plan

## Current decision

Status: `BLOCKED — CANONICAL REPOSITORY, CHARTER, SECURITY, PROVENANCE, AND APPROVAL REQUIRED`

No release is ready. `aevespers2/ALISTAIRE-` contains the established product directive and now has a Pages-ready documentation candidate, while `aevespers2/Alistaire-agi` presents the same Alistaire/QSO identity, the proposed package name `alistaire-qso`, duplicate coordination records, and a broad mostly empty documentation scaffold. P0 remains blocked on selection of one canonical repository and an approved migration/redirect/archive plan before charter completion or runtime work.

The documentation candidate improves project overview, architecture, responsibility boundaries, repository consolidation, security/governance, onboarding, diagrams, and validation. It is review evidence only. No executable AGI, autonomous-learning, deployment, test, security, provenance, or production capability is established.

## Versioning

- Scheme: Semantic Versioning after canonical repository selection.
- First eligible candidate: `0.0.1-charter` in the approved canonical repository.
- The `charter` label denotes documentation and contract proposals only; it must not imply executable AGI, consciousness, sentience, autonomous learning, or production readiness.
- The non-canonical repository must not publish a competing package or release identity.
- `alistaire-qso` remains a proposed package identifier until explicitly approved.
- Any executable candidate requires a later version after the charter and upstream QSO contracts are approved and verified.

## Candidate scope

The first candidate is documentation-only and may include:

- canonical repository, final repository name, package/display name, migration map, redirects/archive notice, and preserved provenance;
- approved product purpose, intended users, product mode, use cases, non-goals, terminology, and prohibited claims;
- authoritative QSO subsystem composition and repository ownership map;
- proposed versioned contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, `Bridge`, and `qsio-kernel`;
- lifecycle, communication, conflict resolution, uncertainty, evidence, consent, freeze, shutdown, rollback, and human-approval flows;
- bounded-learning policy covering allowed sources, persistence, privacy, time, resource, size, and network limits;
- threat model, credential boundary, external-tool restrictions, and misuse/abuse analysis;
- deterministic evaluation and adversarial-fixture specification;
- one consolidated GitHub Pages documentation map, onboarding, limitations, provenance, and review instructions.

Runtime code, external data ingestion, persistent learning, autonomous tool use, deployment, and production capability claims are outside this candidate.

## Selected completed work

- `taskchain.md` defines the evidence-bounded charter direction, active chain, and duplicate-repository hold.
- `punchlist.md` decomposes canonical-repository selection, charter work, documentation validation, security/privacy review, provenance, artifact, and rollback requirements.
- `changelog.md` records the product coordination state and documentation milestone.
- `README.md` provides a polished project overview, responsibility map, documentation navigation, and explicit non-capabilities.
- `docs/` now contains a bounded charter overview, architecture, subsystem ownership matrix, lifecycle, message and learning constraints, security/governance model, consolidation inventory and recommendation, onboarding, and diagrams.
- `mkdocs.yml`, pinned documentation requirements, and a least-permission workflow provide exact-head strict site validation and a checksummed review artifact.
- `Alistaire-agi` remains an observed source of the package-name proposal and placeholder topic taxonomy that must be inventoried during consolidation.

These items establish a substantial documentation candidate. They do not complete P0, approve the recommendation, validate upstream contracts, establish runtime capability, or satisfy release evidence gates.

## Consolidation recommendation

The candidate recommends retaining `ALISTAIRE-` as the canonical charter-history authority because it contains the first substantive directive, roadmap, release controls, punch list, and evidence trail. It recommends preserving `alistaire-qso` as a package-name proposal and treating the empty `Alistaire-agi/docs/**` tree as a backlog taxonomy rather than completed documentation.

This recommendation requires explicit approval and may be replaced by another disposition with an equivalent provenance and rollback plan.

## Acceptance gates

| Gate | Status | Requirement |
|---|---|---|
| Consolidation evidence | REVIEW | Inventory, criteria, options, recommendation, migration map, and approval template exist; verify completeness against both repository histories. |
| Canonical repository | BLOCKED | Select canonical repository/final name/package identity and approve migration, provenance, license, redirect/archive, rollback, and non-canonical role. |
| Task completion | FAIL | Complete and evidence every blocking item in `punchlist.md`; mark the corresponding task-chain work `DONE`. |
| Charter completeness | PARTIAL | Proposed purpose, local simulation mode, non-goals, QSO responsibilities, lifecycle, learning, consent, and failure boundaries exist but are not approved. |
| Dependency contracts | NO EVIDENCE | Upstream repositories and immutable candidate versions are identified and validated without overlapping ownership. |
| Documentation validation | PENDING | Exact pull-request head passes strict MkDocs build, link/navigation review, diagram review, terminology review, and checksummed artifact retention. |
| Deterministic evaluation | NO EVIDENCE | Positive, negative, adversarial, consent, identity, memory, policy, resource, freeze, recovery, and rollback fixtures are specified and reproduced. |
| Security and privacy | PARTIAL | Threat, trust-boundary, consent, privacy, capability, learning, incident, and release-blocking controls are proposed; independent review and evidence remain absent. |
| Provenance and reproducibility | PARTIAL | Source repositories and observed commits are documented; complete migration manifest, environment, artifacts, checksums, attestations, and approval record remain. |
| Rollback and shutdown | PARTIAL | Proposed freeze, shutdown, incident, and consolidation rollback paths exist; drills and immutable evidence are absent. |
| Approval | PENDING | Explicit release approval is recorded only after every blocking gate passes. |

## Artifact requirements

- Canonical-repository decision and migration/provenance map.
- Redirect/archive notice or approved non-overlapping role for the non-canonical repository.
- Approved product/architecture charter.
- QSO responsibility and ownership matrix.
- Versioned dependency/contract manifest.
- Architecture, trust-boundary, evidence-flow, freeze/shutdown, and rollback diagrams.
- Security/privacy threat model and review report.
- Deterministic evaluation and adversarial-fixture specification.
- Exact-head strict documentation output and SHA-256 manifest.
- Source/rendered documentation archive, provenance manifest, rollback evidence, and approval record.

## Validation target

The documentation workflow must:

1. check out and assert the exact submitted head;
2. use read-only repository permission and no persisted checkout credentials;
3. install only the pinned documentation dependencies;
4. run `mkdocs build --strict`;
5. hash the rendered site and configuration;
6. retain a review artifact tied to the exact head.

A passing workflow validates documentation construction only. It does not authorize Pages publication, package release, runtime, network, credentials, tools, persistence, or deployment.

## Rollback criteria

Withdraw the candidate if two repositories continue publishing competing identities, migration loses history or attribution, documentation validation is non-reproducible, dependency ownership conflicts remain, security/privacy boundaries are incomplete, learning/tool authority exceeds the charter, consent or freeze/shutdown behavior is ambiguous, capability claims exceed evidence, approvals are missing, or artifact hashes differ. Restore the last reviewed state, retain failed-candidate evidence, and do not begin runtime work from an unapproved charter.

## Unresolved blockers

- Canonical Alistaire repository, final repository name, package identity, license, and public notice are not approved.
- Migration, redirect/archive, provenance, and rollback plans require explicit disposition.
- Most `punchlist.md` items remain incomplete; only bounded inventory and documentation-candidate preparation have advanced to review.
- No accepted upstream contract manifest, runtime, deterministic evaluation harness, complete security/privacy review, release provenance bundle, rollback drill, or approval exists.
- Runtime remains blocked behind QSO-GENOMES and QuantumStateObjects baselines.
- Product mode, QSO ownership, learning/persistence/privacy, freeze/shutdown behavior, and first executable operating mode require approval.

## Release log

- 2026-07-20: Added a substantial Pages-ready charter and repository-consolidation documentation candidate. The candidate recommends `ALISTAIRE-` as charter-history authority, but P0 and release remain blocked pending explicit approval and exact-head validation.
- 2026-07-16: Reconciled the newly added punch list; the documentation-only candidate remained blocked with no release promoted.
- 2026-07-16: Added the canonical-repository consolidation gate after creation of overlapping `Alistaire-agi`; no release or runtime work approved.
