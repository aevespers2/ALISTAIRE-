# Punch List

Checked items require reviewable evidence tied to immutable commits. Empty files, filenames, diagrams-as-ideas, or capability statements are not completion evidence.

## P0 — Canonical repository decision

- [ ] Inventory `aevespers2/ALISTAIRE-` and `aevespers2/Alistaire-agi` by file, substance, commit history, issues, and release claims.
- [ ] Select one canonical repository and package/display name.
- [ ] Approve migration, preserved-history, attribution, redirect/archive, and rollback plan.
- [ ] Define any non-overlapping role for the non-canonical repository or mark it retired.
- [ ] Confirm license and public-notice requirements.

## P1 — Product and architecture charter

- [ ] Approve product mode, intended users, use cases, non-goals, and prohibited claims.
- [ ] Define QSO subsystem responsibilities, inputs, outputs, state, failure modes, and owner repositories.
- [ ] Pin upstream contract candidates or mark them blocked without guessing.
- [ ] Define lifecycle, communication, conflict resolution, uncertainty, evidence, freeze, shutdown, and rollback.
- [ ] Define bounded learning, persistence, privacy, resource, time, size, network, and approval limits.
- [ ] Define external-tool, credential, and publication boundaries.

## P2 — Documentation and evaluation evidence

- [ ] Consolidate substantive documentation and remove or clearly label placeholders.
- [ ] Validate internal links, terminology, Mermaid diagrams, schema examples, and dependency references.
- [ ] Specify deterministic positive, negative, adversarial, freeze, recovery, identity, memory, and policy fixtures.
- [ ] Produce security/privacy threat model and prohibited-claim review.
- [ ] Record limitations and distinguish implemented, planned, hypothetical, and prohibited capabilities.

## P3 — Candidate release evidence

- [ ] Reproduce all checks from a clean checkout at one immutable commit.
- [ ] Record tool/dependency versions, commands, outputs, and environment.
- [ ] Generate source/rendered documentation artifacts and SHA-256 checksums.
- [ ] Produce provenance manifest covering both source repositories and migration.
- [ ] Perform repository-consolidation and failed-candidate rollback drills.
- [ ] Record explicit approval for `0.0.1-charter`.

## Evidence log

Record date, task, repositories/commits, commands, environment, result (`PASS`, `FAIL`, or `UNKNOWN`), artifacts/hashes, limitations, reviewer, rollback, and follow-up work.