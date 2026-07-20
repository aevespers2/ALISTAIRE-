# Punch List

Checked items require reviewable evidence tied to immutable commits. Empty files, filenames, diagrams-as-ideas, workflow configuration without a successful run, or capability statements are not completion evidence.

## P0A — Consolidation evidence candidate

- [x] Inventory the substantive coordination content in `aevespers2/ALISTAIRE-`.
- [x] Inventory the proposed package identity and mostly empty topic scaffold in `aevespers2/Alistaire-agi`.
- [x] Document decision criteria, migration options, costs, risks, and rollback considerations.
- [x] Prepare a recommendation without silently selecting authority.
- [x] Prepare an approval-record template and proposed migration map.
- [ ] Validate the inventory against both complete repository histories and record exact source commits in a provenance manifest.
- [ ] Obtain human disposition of the recommendation.

## P0 — Canonical repository decision

- [ ] Select one canonical repository and final repository name.
- [ ] Approve package/display identity, including disposition of `alistaire-qso`.
- [ ] Approve migration, preserved-history, attribution, redirect/archive, and rollback plan.
- [ ] Define any non-overlapping role for the non-canonical repository or mark it retired.
- [ ] Confirm license and public-notice requirements.

## P1 — Product and architecture charter

- [ ] Approve product mode, intended users, use cases, non-goals, and prohibited claims.
- [ ] Approve QSO subsystem responsibilities, inputs, outputs, state, failure modes, and owner repositories.
- [ ] Pin upstream contract candidates or mark them blocked without guessing.
- [ ] Approve lifecycle, communication, conflict resolution, uncertainty, evidence, freeze, shutdown, and rollback.
- [ ] Approve bounded learning, persistence, privacy, consent, resource, time, size, network, and review limits.
- [ ] Approve external-tool, credential, write, publication, and deployment boundaries.

## P2 — Documentation and evaluation evidence

- [x] Add a substantive Pages-ready overview and documentation map.
- [x] Add proposed architecture, subsystem ownership, lifecycle, trust-boundary, evidence-flow, and rollback documentation.
- [x] Add repository-consolidation inventory, recommendation, migration map, and decision template.
- [x] Add security/privacy, consent, capability, learning, incident, and governance guidance.
- [x] Add developer/reviewer onboarding and evidence discipline.
- [x] Add strict MkDocs configuration and pinned documentation dependencies.
- [x] Add exact-head, read-only documentation validation and checksummed artifact workflow.
- [ ] Validate the exact pull-request head with `mkdocs build --strict` and retain the artifact/digest.
- [ ] Review internal links, terminology, diagrams, accessibility, schema examples, and dependency references.
- [ ] Specify deterministic positive, negative, adversarial, freeze, recovery, identity, memory, policy, consent, and resource fixtures.
- [ ] Complete independent security/privacy and prohibited-claim review.
- [ ] Record limitations and classify every public capability as observed, implemented, verified, proposed, hypothetical, or prohibited.

## P3 — Candidate release evidence

- [ ] Reproduce all checks from a clean checkout at one immutable commit.
- [ ] Record tool/dependency versions, commands, outputs, and environment.
- [ ] Generate source/rendered documentation artifacts and SHA-256 checksums.
- [ ] Produce a provenance manifest covering both source repositories and migration.
- [ ] Perform repository-consolidation and failed-candidate rollback drills.
- [ ] Record explicit approval for `0.0.1-charter`.

## Evidence log

### 2026-07-20 — Documentation and consolidation candidate

- Repositories: `aevespers2/ALISTAIRE-`, `aevespers2/Alistaire-agi`
- Branch: `docs/consolidation-charter-20260720`
- Result: `REVIEW`
- Added: README, strict MkDocs site, architecture, consolidation decision, security/governance, onboarding, diagrams, workflow, and coordination-file reconciliation.
- Recommendation: retain `ALISTAIRE-` as charter-history authority and preserve `alistaire-qso` as a package-name proposal, subject to explicit approval.
- Limitations: no exact-head workflow result yet; complete history inventory, license, migration/provenance manifest, approval, upstream contract pinning, evaluation fixtures, runtime, and release evidence remain incomplete.
- Rollback: close the candidate and delete the branch; neither repository identity nor runtime state is changed by the documentation branch.
