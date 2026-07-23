# D1 canonical identity decision packet

Status: **review ready, decision blocked**

This packet converts the repository-identity conflict into a closed review surface. It does not select a canonical repository, approve a package or license, authorize migration, rename or archive a repository, publish Pages, release software, or expand implementation authority.

The machine-readable companion is [`d1-canonical-identity-decision-packet-v1.json`](d1-canonical-identity-decision-packet-v1.json).

## Why D1 remains blocked

The evidence supports a working recommendation, but several required decision inputs remain absent: a complete path-level migration manifest, a license decision, history-aware secret and privacy review, named support/security/rollback owners, a compatibility and redirect plan, a rollback drill, and explicit human approval bound to an immutable source head.

```text
repository inventories
+ exact source tuples
+ provenance and classification
+ options and recommendation
+ migration, license, ownership, compatibility, and rollback evidence
+ explicit immutable approval
= D1 decision record
```

**Equivalent prose:** inventories and a recommendation can make D1 reviewable, but they cannot decide it. The decision becomes eligible only when every required field and evidence gate is complete, an authorized human records the disposition at an immutable head, and rollback remains possible.

## Bound source observations

| Repository | Observed default head | Documentation candidate | Current evidence role |
|---|---|---|---|
| `aevespers2/ALISTAIRE-` | `7adbbf963616d09b4ebafea7c0963a2fac5688a9` | PR #1 baseline `f3cd97c2418c87f6c4aa7cac7731460ed57f13b7` | candidate charter-history authority |
| `aevespers2/Alistaire-agi` | `504222dbecb1e1e49c01d74e536de5b6fa93c39a` | PR #2 head `0ede0c6a796fe9f16c10d25fc79ba6962875ba82` | compatibility, migration, and taxonomy candidate |

A moved, closed, superseded, or contradicted source requires `D1_REBIND_REQUIRED`. A withdrawn packet requires `D1_PACKET_WITHDRAWN` on every controlled route.

## Decision options

### Option A — retain `ALISTAIRE-` as the charter-history authority

**Working recommendation, not selection.** This option preserves the strongest substantive charter, release-control, governance, and provenance history. It still requires a clean final repository name, package disposition, path-level migration, license, compatibility notice, non-canonical outcome, owner assignments, and rollback evidence.

### Option B — use `Alistaire-agi` as canonical

This option has a cleaner current repository name and a broad taxonomy, but requires migrating the substantive charter and release history, preserving attribution, classifying placeholder paths, and preventing the old repository from remaining a parallel authority.

### Option C — split responsibilities

This option is not recommended before distinct implementation responsibilities exist. A split now would preserve two product identities and two possible release authorities rather than close the obstruction.

## Required immutable decision fields

A valid D1 record must state:

1. canonical repository and final repository name;
2. display name and package identifier or explicit package deferral;
3. license or explicit no-reuse status;
4. canonical documentation and release authority;
5. non-canonical repository disposition;
6. path-level migration, exclusion, attribution, and history-preservation manifest;
7. compatibility window and public notice;
8. support and security-reporting routes;
9. redirect, archive, rename, or bounded-role plan;
10. post-transition monitoring and rollback plan;
11. approver identity, approval date, and approved immutable head.

## Current readiness

| Gate | State |
|---|---|
| Repository inventory | Satisfied |
| Provenance manifest | Satisfied for documentation review only |
| Reciprocal source binding | Satisfied for documentation review only |
| Options and recommendation | Satisfied for documentation review only |
| Complete path-level migration manifest | Missing |
| License decision | Missing |
| History-aware secret and privacy review | Missing |
| Support, security, compatibility, and rollback owners | Missing |
| Compatibility and redirect plan | Missing |
| Rollback drill | Missing |
| Explicit human approval | Missing |

Current disposition: `BLOCKED_MISSING_DECISION_EVIDENCE_AND_APPROVAL`.

## Controlled-route propagation

The root README, repository-consolidation guide, this packet, task chain, punch list, release plan, and changelog must agree on the same D1 state. A correction is incomplete while any route still presents stale source identities, a superseded recommendation, an outdated readiness state, or an unsupported approval claim.

## Fail-closed rules

- A recommendation is not canonical selection.
- Passing CI is not approval.
- Mergeability is not authority.
- A package name is not package ownership.
- Copied content does not establish license permission.
- A documentation candidate is not release authority.
- Closing or merging a candidate does not prove resulting repository settings, redirects, archives, or rollback readiness.

## FYSA-120 capability map

Applied categories:

- CAT-012 — document architecture, decision-record writing, documentation testing, and lifecycle synchronization;
- CAT-013 — entity resolution, canonical identifier design, contradiction detection, provenance, and graph validation;
- CAT-017 — canonical-version resolution, derivation chains, version-substitution detection, hashing, and correction propagation;
- CAT-018 — decision memory, record classification, authenticity preservation, responsibility mapping, and onboarding transfer;
- CAT-031 — invariant definition, threat-aware acceptance criteria, regression validation, verified builds, and assurance maintenance;
- CAT-040 — system archaeology, migration dependency mapping, compatibility-layer design, cutover planning, integrity verification, and rollback;
- CAT-052 — trust modeling, least privilege, audit evidence, and continuous assurance.

Proposed non-authoritative subdivision: **`040-G — Canonical-source decision readiness and reversible dual-authority cutover`**.

## Authority boundary

This packet prepares a bounded decision. It creates no canonical repository, package, license, maintainer appointment, merge authority, release authority, publication approval, deployment authority, migration execution, repository-setting change, or operational capability.
