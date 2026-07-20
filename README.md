# Alistaire

Alistaire is a **documentation-first research architecture** for composing a bounded agent system from interoperable Quantum State Objects (QSOs). This repository currently owns the product-level charter and review boundary; it does **not** contain or claim a verified AGI runtime, consciousness, autonomous learning, production deployment, or unrestricted tool authority.

> **Current status: blocked on repository identity.** `aevespers2/ALISTAIRE-` and `aevespers2/Alistaire-agi` overlap. One canonical repository, package/display name, migration plan, and non-canonical disposition must be approved before a charter release or runtime task becomes eligible.

## Documentation

- [Project overview](docs/index.md)
- [Architecture and QSO composition](docs/architecture.md)
- [Repository consolidation decision](docs/repository-consolidation.md)
- [Security, privacy, and governance](docs/security-and-governance.md)
- [Developer and reviewer onboarding](docs/development.md)
- [Architecture diagrams](docs/diagrams.md)
- [Task chain](taskchain.md)
- [Release plan](release.md)
- [Punch list](punchlist.md)
- [Changelog](changelog.md)

## Repository responsibility

This repository is presently the **candidate charter authority**. It defines product scope, ownership boundaries, evidence classes, safety invariants, release gates, and the proposed composition of existing QSO repositories. It must not duplicate their implementation responsibilities.

| Repository | Proposed responsibility |
|---|---|
| `QuantumStateObjects` | Runnable QSO primitives, lifecycle semantics, and local deterministic baseline |
| `QSO-GENOMES` | Declarative identity, traits, immutable policy, lineage, and compatibility contracts |
| `QSO-FABRIC` | Bounded multi-QSO collaboration and experiment orchestration |
| `QSO-SEEKER` | Hostile-input retrieval boundary, sanitization, canonical records, and attribution |
| `QSO-STUDIO` | Human-facing inspection, annotation, proposal, and evidence-review surfaces |
| `Bridge` | Explicitly authorized cross-system transport and integration boundaries |
| `qsio-kernel` | Kernel-level shared interfaces only after contracts are accepted and pinned |

All assignments above are documentation proposals until the canonical repository and upstream contract decisions are approved.

## Near-term scope

The first eligible candidate is `0.0.1-charter`, a documentation-only release containing:

1. canonical repository and naming decision;
2. preserved-history migration and redirect/archive plan;
3. approved product and architecture charter;
4. QSO responsibility and contract map;
5. bounded learning, persistence, tool, credential, privacy, freeze, shutdown, and rollback policies;
6. deterministic evaluation and adversarial-fixture specification;
7. validated GitHub Pages documentation and provenance evidence.

## Explicit non-capabilities

Until later implementation and evidence gates pass, Alistaire has no authorized network access, credentials, external-tool execution, private-data ingestion, persistent self-modification, autonomous publication, deployment authority, or production safety claim. Empty or placeholder files in either Alistaire repository are inventory—not evidence of implemented capability.

## Local documentation preview

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
mkdocs serve
```

The documentation workflow validates the site with `mkdocs build --strict`; it does not deploy or release an application.
