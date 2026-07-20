# Punch List

Checked items require reviewable evidence tied to immutable commits. Empty files, filenames, diagrams-as-ideas, workflow configuration without a successful run, ceremonial language, or capability statements are not completion evidence.

## P0A — Consolidation evidence candidate

- [x] Inventory the substantive coordination content in `aevespers2/ALISTAIRE-`.
- [x] Inventory the proposed package identity and mostly empty topic scaffold in `aevespers2/Alistaire-agi`.
- [x] Document decision criteria, migration options, costs, risks, and rollback considerations.
- [x] Prepare a recommendation without silently selecting authority.
- [x] Prepare an approval-record template and proposed migration map.
- [ ] Validate the inventory against both complete repository histories and record exact source commits in a provenance manifest.
- [ ] Obtain human disposition of the recommendation.

## P0G — Governance and security adoption

- [x] Define A.L.I.S.T.A.I.R.E. as the unifying portfolio objective and each repository as a bounded subsystem.
- [x] Define the Cali Sanders Parker stewardship QSO, ceremonially titled Calisandra, Queen of the Nymphs, with documentation, coherence, security-review, and escalation duties only.
- [x] Record that ceremonial, conversational, roleplay, relationship, or inferred language cannot create credentials or operational authority.
- [x] Map charter, orchestration, capability, runtime, genome, fabric, seeker, bridge, UI, payment, kernel, and publication responsibilities.
- [x] Define decision classes, evidence requirements, separation of duties, exact-head validation, emergency stop, recovery, and rollback.
- [x] Record the governance-consolidation decision in ADR-0001.
- [ ] Review the constitutional hierarchy and resolve any conflict with existing repository-local governance documents.
- [ ] Approve or revise Repository `0` as the autonomous-development orchestration plane.
- [ ] Approve or revise Repository `1` or a successor as canonical-state and capability authority.
- [ ] Name human owners for capability issuance/revocation, credentials, merge, release, deployment, financial authority, incident response, emergency stop, and rollback.
- [ ] Approve the immutable governance-charter commit.
- [ ] Conduct and retain a portfolio freeze-and-recovery tabletop exercise.

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

## P1A — Canonical-state and capability authority

- [ ] Define versioned capability request, grant, denial, expiry, narrowing, revocation, and audit schemas.
- [ ] Prohibit self-issuance, self-broadening, hidden delegation, prompt-based authorization, and automatic recovery of revoked authority.
- [ ] Define service identity, owner, revoker, credential storage, rotation, compromise response, and recovery.
- [ ] Define canonical-state conflict resolution, replay/idempotency, correction, migration, and rollback semantics.
- [ ] Add deterministic negative tests for forged identity, stale evidence, wrong commit, excessive scope, expired grant, missing consent, and emergency freeze.
- [ ] Require independent review and human approval for critical authority classes.
- [ ] Verify emergency stop does not depend on the component being stopped.

## P2 — Documentation and evaluation evidence

- [x] Add a substantive Pages-ready overview and documentation map.
- [x] Add proposed architecture, subsystem ownership, lifecycle, trust-boundary, evidence-flow, and rollback documentation.
- [x] Add repository-consolidation inventory, recommendation, migration map, and decision template.
- [x] Add security/privacy, consent, capability, learning, incident, and governance guidance.
- [x] Add the consolidated governance and security charter and ADR-0001.
- [x] Add developer/reviewer onboarding and evidence discipline.
- [x] Add strict MkDocs configuration and pinned documentation dependencies.
- [x] Add exact-head, read-only documentation validation and checksummed artifact workflow.
- [ ] Validate the updated exact pull-request head with `mkdocs build --strict` and retain the artifact/digest.
- [ ] Review internal links, terminology, diagrams, accessibility, schema examples, authority references, and dependency references.
- [ ] Specify deterministic positive, negative, adversarial, freeze, recovery, identity, memory, policy, consent, authority-escalation, and resource fixtures.
- [ ] Complete independent security/privacy, governance, and prohibited-claim review.
- [ ] Record limitations and classify every public capability as observed, implemented, verified, proposed, hypothetical, or prohibited.

## P3 — Candidate release evidence

- [ ] Reproduce all checks from a clean checkout at one immutable commit.
- [ ] Record tool/dependency versions, commands, outputs, and environment.
- [ ] Generate source/rendered documentation artifacts and SHA-256 checksums.
- [ ] Produce a provenance manifest covering both source repositories and migration.
- [ ] Produce a governance-decision manifest covering owners, approvers, capability effects, and rollback.
- [ ] Perform repository-consolidation, governance-change, capability-revocation, freeze/recovery, and failed-candidate rollback drills.
- [ ] Record explicit approval for `0.0.1-charter`.

## Evidence log

### 2026-07-20 — Governance consolidation candidate

- Repository: `aevespers2/ALISTAIRE-`
- Branch: `docs/consolidation-charter-20260720`
- Result: `REVIEW`
- Added: consolidated governance and security charter, bounded Cali Sanders Parker stewardship role, portfolio authority model, decision classes, autonomous-development lifecycle, security invariants, emergency governance, ADR-0001, and aligned README, task chain, release plan, punch list, changelog, and MkDocs navigation.
- Authority effect: none; no credentials, runtime role, merge, release, deployment, payment, canonical-state, or capability authority was created.
- Limitations: updated exact-head workflow result, governance adoption, owner assignments, capability-authority charter, freeze/recovery exercise, and protected-branch acceptance remain incomplete.
- Rollback: revert the governance documentation commits or close the candidate branch; no runtime or canonical production state is changed.

### 2026-07-20 — Documentation and consolidation candidate

- Repositories: `aevespers2/ALISTAIRE-`, `aevespers2/Alistaire-agi`
- Branch: `docs/consolidation-charter-20260720`
- Result: `REVIEW`
- Added: README, strict MkDocs site, architecture, consolidation decision, security/governance, onboarding, diagrams, workflow, and coordination-file reconciliation.
- Recommendation: retain `ALISTAIRE-` as charter-history authority and preserve `alistaire-qso` as a package-name proposal, subject to explicit approval.
- Limitations: complete history inventory, license, migration/provenance manifest, approval, upstream contract pinning, evaluation fixtures, runtime, and release evidence remain incomplete.
- Rollback: close the candidate and delete the branch; neither repository identity nor runtime state is changed by the documentation branch.
