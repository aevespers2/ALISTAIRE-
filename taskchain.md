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
- contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, and `Bridge`;
- lifecycle states, bounded learning, freeze points, rollback, and human-approval gates;
- inter-QSO communication, conflict resolution, provenance, and uncertainty handling;
- security and privacy threat models, credential boundaries, and external-tool restrictions;
- deterministic evaluation fixtures and a staged test plan for identity consistency, memory integrity, policy compliance, recovery, and bounded adaptation;
- one consolidated documentation map and repository-onboarding path.

### Priority

**Repository priority: P0 — BLOCKED (canonical repository approval required).**

This is a documented scope conflict created by the new overlapping `Alistaire-agi` repository. The hold prevents parallel charters and duplicate implementation; it does not supersede the active QSO-GENOMES contract work or the QuantumStateObjects runnable-baseline objective. Runtime implementation remains blocked until upstream contracts are stable, the canonical repository is selected, and the charter is approved.

### Success criteria

- One canonical Alistaire repository and package/release identity are approved.
- Useful content and history from both repositories are inventoried, migrated or linked, and preserved with attribution.
- The non-canonical repository is redirected, archived, or assigned a clearly non-overlapping responsibility.
- The charter distinguishes implemented capabilities, planned capabilities, hypotheses, placeholder documentation, and prohibited claims.
- Every proposed QSO subsystem has a declared responsibility, inputs, outputs, state, failure modes, and owner repository.
- Architecture diagrams show composition, data/control flow, trust boundaries, evidence flow, and shutdown/rollback paths.
- Learning and adaptation are bounded by explicit policy, resource, time, size, privacy, and approval limits.
- Evaluation criteria are deterministic where practical and include negative/adversarial fixtures.
- The dependency map identifies versioned contracts and does not duplicate responsibilities already assigned to another repository.
- A documentation-only release can be reviewed without implying that an AGI runtime exists.

### Non-goals

- Implementing or deploying an unrestricted autonomous agent.
- Claiming consciousness, sentience, AGI, or human-equivalent cognition without validated evidence.
- Treating a large empty documentation tree as completed design or capability.
- Silent self-modification, credential discovery, remote writes, deployment, or publication.
- Reimplementing QSO runtime, genome, fabric, seeker, studio, or Bridge capabilities inside Alistaire.
- Training on private or external data without explicit provenance, consent, and policy controls.
- Shipping a user-facing production application before contracts, fixtures, tests, security review, and rollback evidence exist.

### Release rationale

A documentation-only consolidation and charter candidate is the safest first release because two repositories now present overlapping Alistaire identities and the runtime spans multiple active QSO repositories. Establishing one authority first prevents duplicated implementation, unsupported AGI claims, incompatible contracts, provenance loss, and premature deployment.

## Approval gates

The Architect must not decompose runtime implementation until approval is recorded for:

1. canonical repository, package/display name, migration, redirect/archive, and provenance plan;
2. product identity: research agent framework, interactive companion, or both;
3. authoritative QSO subsystem list and repository ownership boundaries;
4. allowed learning sources, persistence model, and privacy policy;
5. freeze, shutdown, rollback, and human-approval behavior;
6. whether the first executable MVP is local-only, simulation-only, or includes a user interface.

## Roadmap

| Priority | Task | Depends on | Status |
|---|---|---|---|
| P0 | Select the canonical Alistaire repository and reconcile both histories | User approval | BLOCKED |
| P1 | Produce and approve the consolidated Alistaire product/architecture charter | P0 | PROPOSED |
| P2 | Define versioned QSO composition and inter-repository contracts | P1, QSO-GENOMES baseline, QuantumStateObjects baseline | PROPOSED |
| P3 | Create deterministic simulation fixtures and evaluation-harness specification | P2 | PROPOSED |
| P4 | Implement a local, bounded, no-network simulation of the composed QSO lifecycle | P3 | PROPOSED |
| P5 | Add reviewed persistence, tool, and interface adapters behind explicit policy gates | P4 | PROPOSED |
| P6 | Produce security, provenance, reproducibility, deployment, and rollback evidence | P5 | PROPOSED |

## Builder rules

Builders execute only `READY` tasks. While P0 is blocked, permitted work is limited to read-only inventory and evidence preservation. No runtime implementation, external data ingestion, autonomous tool use, deployment, or capability claim is authorized.

## Evidence rules

For every task, record:

- observations;
- proposals or hypotheses;
- implemented artifacts;
- validation results (`PASS`, `FAIL`, or `UNKNOWN`);
- source repositories, commits, and dependency versions;
- commands, environment, tests, and artifact hashes;
- limitations, residual risks, migration map, and rollback instructions.