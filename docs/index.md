# Alistaire charter candidate

Alistaire is a proposed female-presenting research agent architecture composed of interoperable Quantum State Objects. The project is currently in a **documentation and repository-consolidation phase**. No executable AGI, consciousness, sentience, unrestricted autonomy, persistent self-improvement, or production deployment is established.

## Decision status

**Blocked:** two repositories currently overlap:

- `aevespers2/ALISTAIRE-` contains the established product directive, task chain, release gates, punch list, and coordination history.
- `aevespers2/Alistaire-agi` contains the proposed `alistaire-qso` package name and a broad, mostly empty documentation scaffold.

The documentation here prepares the evidence needed to select one canonical repository without silently discarding either history. It does not make that approval decision.

## Intended outcome

After approval, a researcher should be able to answer:

- What is Alistaire for, and what is explicitly outside scope?
- Which QSO subsystem owns identity, memory, goals, policy, planning, evidence, perception, and tool proposals?
- Which repository owns each contract and implementation surface?
- What information may be learned, persisted, shared, or forgotten?
- Where do human confirmation, consent, freeze, shutdown, and rollback apply?
- What deterministic evidence is required before any capability claim or release?

## Proposed product mode

The safest initial mode is a **local, simulation-only research orchestrator**. It composes accepted QSO contracts, evaluates bounded scenarios, records provenance and uncertainty, and produces reviewable proposals. It has no network, credentials, external writes, or self-authorized execution.

A future interactive companion or broader research assistant would require a separate approval cycle covering identity expectations, privacy, consent, retention, tool authority, evaluation, deployment, and incident response.

## Documentation map

| Guide | Purpose |
|---|---|
| [Architecture](architecture.md) | Proposed subsystem composition, lifecycle, contracts, ownership, and evidence flow |
| [Repository consolidation](repository-consolidation.md) | Inventory findings, decision criteria, migration options, and recommendation |
| [Security and governance](security-and-governance.md) | Assets, threats, trust boundaries, consent, privacy, learning limits, and stop conditions |
| [Developer onboarding](development.md) | Documentation workflow, evidence discipline, contribution boundaries, and review checklist |
| [Diagrams](diagrams.md) | Component, lifecycle, trust-boundary, dependency, and rollback diagrams |

## Evidence vocabulary

Every statement should be classified as one of:

- **Observed:** directly present in a repository, commit, workflow, artifact, or accepted contract.
- **Implemented:** code or data exists, but may still require independent validation.
- **Verified:** reproduced at an immutable commit with retained evidence.
- **Proposed:** design requiring approval or implementation.
- **Hypothesis:** research idea without accepted evidence.
- **Prohibited:** outside the current authority boundary.

Repository names, empty pages, future-facing terminology, and architectural diagrams are not implementation evidence.

## Release posture

The first possible release is `0.0.1-charter`. It is documentation-only and remains blocked until canonical repository selection, migration/provenance planning, charter approval, security/privacy review, documentation validation, artifact hashing, rollback evidence, and explicit approval are complete.
