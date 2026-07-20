# Task Chain

## Product directive

### Next product objective

Resolve the canonical repository and product-identity conflict between **`aevespers2/ALISTAIRE-`** and **`aevespers2/Alistaire-agi`**, then complete one evidence-bounded product and architecture charter for Alistaire as a female-presenting agent system composed of interoperable Quantum State Objects (QSOs).

The charter must translate the concept into explicit contracts, evaluation criteria, safety boundaries, repository responsibilities, and evidence rules without claiming that AGI, consciousness, autonomy, or production readiness has already been implemented.

### Intended user outcome

A researcher or Architect can identify one authoritative repository and understand exactly what Alistaire is intended to do, which QSO subsystems compose her, how those subsystems communicate and learn, where freeze/stop controls apply, what evidence is required for capability claims, and which existing repositories supply each dependency.

### MVP scope

The first candidate is documentation-only and must define:

- canonical repository, package/display name, migration/redirect/archive decision, and preserved provenance;
- product purpose, primary users, use cases, product mode, and non-goals;
- a QSO composition map for identity/persona, goals, memory, beliefs, ethics/policy, perception, planning, tool use, reflection, and evidence;
- contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, `Bridge`, and `qsio-kernel`;
- lifecycle states, bounded learning, freeze points, rollback, and human-approval gates;
- inter-QSO communication, conflict resolution, provenance, and uncertainty handling;
- security and privacy threat models, consent, credential boundaries, and external-tool restrictions;
- deterministic evaluation fixtures and a staged test plan for identity consistency, memory integrity, policy compliance, recovery, and bounded adaptation;
- one consolidated documentation map and repository-onboarding path.

### Priority

**Repository priority: P0 — BLOCKED (canonical repository approval required).**

The documentation candidate now supplies an inventory, decision criteria, migration options, a recommendation, a bounded architecture, security/governance boundaries, onboarding, and diagrams. This advances evidence preparation but does not approve the canonical repository, package identity, product mode, upstream contracts, runtime, or release.

The hold prevents parallel charters and duplicate implementation; it does not supersede active QSO-GENOMES contract work or the QuantumStateObjects runnable-baseline objective. Runtime implementation remains blocked until upstream contracts are stable, the canonical repository is selected, and the charter is approved.

### Success criteria

- One canonical Alistaire repository and package/release identity are approved.
- Useful content and history from both repositories are inventoried, migrated or linked, and preserved with attribution.
- The non-canonical repository is redirected, archived, or assigned a clearly non-overlapping responsibility.
- The charter distinguishes implemented capabilities, planned capabilities, hypotheses, placeholder documentation, and prohibited claims.
- Every proposed QSO subsystem has a declared responsibility, inputs, outputs, state, failure modes, and owner repository.
- Architecture diagrams show composition, data/control flow, trust boundaries, evidence flow, and shutdown/rollback paths.
- Learning and adaptation are bounded by explicit policy, resource, time, size, privacy, consent, and approval limits.
- Evaluation criteria are deterministic where practical and include negative/adversarial fixtures.
- The dependency map identifies versioned contracts and does not duplicate responsibilities already assigned to another repository.
- A documentation-only release can be reviewed without implying that an AGI runtime exists.

### Non-goals

- Implementing or deploying an unrestricted autonomous agent.
- Claiming consciousness, sentience, AGI, or human-equivalent cognition without validated evidence.
- Treating a large empty documentation tree as completed design or capability.
- Silent self-modification, credential discovery, remote writes, deployment, or publication.
- Reimplementing QSO runtime, genome, fabric, seeker, studio, Bridge, or kernel capabilities inside Alistaire.
- Training on private or external data without explicit provenance, consent, and policy controls.
- Shipping a user-facing production application before contracts, fixtures, tests, security review, and rollback evidence exist.

### Release rationale

A documentation-only consolidation and charter candidate is the safest first release because two repositories now present overlapping Alistaire identities and the runtime spans multiple active QSO repositories. Establishing one authority first prevents duplicated implementation, unsupported AGI claims, incompatible contracts, provenance loss, and premature deployment.

## Current evidence state

### Observed

- `ALISTAIRE-` contains the first substantive product directive, release gates, punch list, and coordination history.
- `Alistaire-agi` contains the proposed package name `alistaire-qso`, duplicate coordination documents, and a broad documentation scaffold created without substantive patches.
- The documentation candidate adds a strict Pages-ready site, architecture and subsystem responsibility matrix, consolidation decision record, security/governance model, onboarding, diagrams, and exact-head documentation validation workflow.
- The consolidation record recommends retaining `ALISTAIRE-` as the charter-history authority and treating `alistaire-qso` as a package-name proposal, subject to explicit approval.

### Not established

- No canonical repository, final repository name, package identity, license, migration, redirect/archive, or provenance plan is approved.
- No upstream QSO contract is pinned as authoritative for Alistaire.
- No runtime, package, deterministic evaluation harness, deployment, or production capability is established.
- Documentation build success is pending at the exact pull-request head until GitHub Actions completes.

## Approval gates

The Architect must not decompose runtime implementation until approval is recorded for:

1. canonical repository, package/display name, migration, redirect/archive, and provenance plan;
2. product identity: research agent framework, interactive companion, or both;
3. authoritative QSO subsystem list and repository ownership boundaries;
4. allowed learning sources, persistence model, consent, and privacy policy;
5. freeze, shutdown, rollback, and human-approval behavior;
6. whether the first executable MVP is local-only, simulation-only, or includes a user interface.

## Active chain

| Priority | Task | Depends on | Status | Acceptance criteria |
|---|---|---|---|---|
| P0A | Inventory both repositories and prepare a consolidation recommendation | — | REVIEW | Substantive files, placeholder files, histories, identities, migration options, risks, and rollback are documented without choosing authority silently. |
| P0 | Select the canonical Alistaire repository and reconcile both histories | P0A, user approval | BLOCKED | Canonical repository, final name, package identity, migration, provenance, license, redirect/archive, rollback, and non-canonical role are approved. |
| P1 | Produce and approve the consolidated Alistaire product/architecture charter | P0 | PROPOSED | Purpose, product mode, users, non-goals, QSO responsibilities, lifecycle, consent, learning, privacy, security, evidence, and prohibited claims are accepted. |
| P2 | Define versioned QSO composition and inter-repository contracts | P1, QSO-GENOMES baseline, QuantumStateObjects baseline | PROPOSED | Accepted immutable contract versions and ownership boundaries are recorded with compatibility and migration rules. |
| P3 | Create deterministic simulation fixtures and evaluation-harness specification | P2 | PROPOSED | Positive, negative, adversarial, identity, memory, policy, consent, freeze, recovery, resource, and rollback fixtures are approved. |
| P4 | Implement a local, bounded, no-network simulation of the composed QSO lifecycle | P3 | PROPOSED | Exact-head implementation passes deterministic and safety tests within resource limits and has retained provenance and rollback evidence. |
| P5 | Add reviewed persistence, tool, and interface adapters behind explicit policy gates | P4 | PROPOSED | Every capability is least-privilege, consent-bound, observable, revocable, separately tested, and off by default. |
| P6 | Produce security, provenance, reproducibility, deployment, and rollback evidence | P5 | PROPOSED | Complete release evidence passes independent review and explicit approval. |

## Builder rules

Builders execute only `READY` tasks. While P0 is blocked, permitted work is limited to read-only inventory, documentation, validation, contract proposals, and evidence preservation. No runtime implementation, external data ingestion, autonomous tool use, deployment, or capability claim is authorized.

## Evidence rules

For every task, record:

- observations;
- proposals or hypotheses;
- implemented artifacts;
- validation results (`PASS`, `FAIL`, or `UNKNOWN`);
- source repositories, commits, and dependency versions;
- commands, environment, tests, and artifact hashes;
- limitations, residual risks, migration map, and rollback instructions.

## Builder log

- 2026-07-20 — Prepared a Pages-ready documentation and charter candidate on `docs/consolidation-charter-20260720`. Added the cross-repository inventory, recommendation, architecture, trust boundaries, security/governance rules, onboarding, diagrams, and exact-head strict documentation workflow. P0 remains blocked pending explicit canonical-repository approval.
