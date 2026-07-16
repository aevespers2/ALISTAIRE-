# Task Chain

## Product Directive

### Next product objective

Define an evidence-bounded product and architecture charter for **Alistaire**, a female-presenting agent system composed of interoperable Quantum State Objects (QSOs). The charter must translate the concept into explicit contracts, evaluation criteria, safety boundaries, and repository responsibilities without claiming that AGI, consciousness, autonomy, or production readiness has already been implemented.

### Intended user outcome

A researcher or Architect can understand exactly what Alistaire is intended to do, which QSO subsystems compose her, how those subsystems communicate and learn, where freeze/stop controls apply, what evidence is required for capability claims, and which existing repositories supply each dependency.

### MVP scope

The first candidate is documentation-only and must define:

- product purpose, primary users, use cases, and non-goals;
- a QSO composition map for identity/persona, goals, memory, beliefs, ethics/policy, perception, planning, tool use, reflection, and evidence;
- contracts with `QuantumStateObjects`, `QSO-GENOMES`, `QSO-FABRIC`, `QSO-SEEKER`, `QSO-STUDIO`, and `Bridge`;
- lifecycle states, bounded learning, freeze points, rollback, and human-approval gates;
- inter-QSO communication, conflict resolution, provenance, and uncertainty handling;
- security and privacy threat models, credential boundaries, and external-tool restrictions;
- deterministic evaluation fixtures and a staged test plan for identity consistency, memory integrity, policy compliance, recovery, and bounded adaptation;
- a documentation map for the future GitHub Pages site and repository onboarding.

### Priority

**Repository priority: P0 — READY (charter only).**

**Portfolio sequencing:** this does not supersede the active QSO-GENOMES contract work or the QuantumStateObjects runnable-baseline objective. Runtime implementation depends on those foundations and remains blocked until their relevant contracts are stable and this charter is approved.

### Success criteria

- The product charter distinguishes implemented capabilities, planned capabilities, hypotheses, and prohibited claims.
- Every proposed QSO subsystem has a declared responsibility, inputs, outputs, state, failure modes, and owner repository.
- Architecture diagrams show composition, data/control flow, trust boundaries, evidence flow, and shutdown/rollback paths.
- Learning and adaptation are bounded by explicit policy, resource, time, size, and approval limits.
- Evaluation criteria are deterministic where practical and include negative/adversarial fixtures.
- The dependency map identifies versioned contracts and does not duplicate responsibilities already assigned to another repository.
- A documentation-only release can be reviewed without implying that an AGI runtime exists.

### Non-goals for this objective

- Implementing or deploying an unrestricted autonomous agent.
- Claiming consciousness, sentience, AGI, or human-equivalent cognition without validated evidence.
- Silent self-modification, credential discovery, remote writes, deployment, or publication.
- Reimplementing QSO runtime, genome, fabric, seeker, studio, or Bridge capabilities inside this repository.
- Training on private or external data without explicit provenance, consent, and policy controls.
- Shipping a user-facing production application before contracts, fixtures, tests, security review, and rollback evidence exist.

### Release rationale

A documentation-only `0.0.1-charter` candidate is the safest first release because the repository is currently empty and the product spans multiple active QSO repositories. Establishing the boundary first prevents duplicated implementation, unsupported AGI claims, incompatible contracts, and premature deployment. A runtime candidate is not eligible until the charter is approved and dependency, test, security, provenance, and operational gates are satisfied.

## Approval Gates

The Architect must not decompose runtime implementation until approval is recorded for:

1. the product identity: research agent framework, interactive companion, or both;
2. the authoritative QSO subsystem list and repository ownership boundaries;
3. allowed learning sources, persistence model, and privacy policy;
4. freeze, shutdown, rollback, and human-approval behavior;
5. whether the first executable MVP is local-only, simulation-only, or includes a user interface.

## Roadmap

| Priority | Task | Depends on | Status |
|---|---|---|---|
| P0 | Produce and approve the Alistaire product/architecture charter | — | READY |
| P1 | Define versioned QSO composition and inter-repository contracts | P0, QSO-GENOMES baseline, QuantumStateObjects baseline | PROPOSED |
| P2 | Create deterministic simulation fixtures and evaluation harness specification | P1 | PROPOSED |
| P3 | Implement a local, bounded, no-network simulation of the composed QSO lifecycle | P2 | PROPOSED |
| P4 | Add reviewed persistence, tool, and interface adapters behind explicit policy gates | P3 | PROPOSED |
| P5 | Produce security, provenance, reproducibility, deployment, and rollback evidence | P4 | PROPOSED |

## Builder Rules

Builders execute only `READY` tasks. P0 permits documentation, diagrams, schemas-as-proposals, fixtures-as-specifications, and repository inventory. It does not authorize runtime implementation, external data ingestion, autonomous tool use, deployment, or capability claims.

## Evidence Rules

For every task, record:

- observations;
- proposals or hypotheses;
- implemented artifacts;
- validation results (`PASS`, `FAIL`, or `UNKNOWN`);
- source commits and dependency versions;
- commands, environment, tests, and artifact hashes;
- limitations, residual risks, and rollback instructions.
