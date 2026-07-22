# A.L.I.S.T.A.I.R.E. Portfolio Contract Standard

## Status

This document is a documentation-stage candidate for a shared interoperability standard. It does not activate a registry, issue authority, select a canonical serializer, bind credentials, or authorize any runtime operation. Adoption requires the constitutional and repository approvals identified in `taskchain.md`.

## Objective

The Portfolio Contract Standard provides one vocabulary and compatibility model for records exchanged across A.L.I.S.T.A.I.R.E. repositories. It prevents repositories from composing by implication, filename coincidence, transport success, or duplicated terminology.

Every cross-repository edge must identify:

- the semantic owner of the record;
- the producer and consumer roles;
- the canonical contract name and version;
- identity, serialization, digest, freshness, replay, and extension rules;
- authority and approval requirements;
- privacy, retention, correction, revocation, and rollback behavior;
- positive, negative, stale, replay, unsupported-version, and partial-failure fixtures.

## Contract families

| Family | Purpose | Candidate semantic owner | Required independence |
|---|---|---|---|
| `portfolio.repository` | Repository identity, role, non-role, and lifecycle | Neutral contract steward | Independent from GitHub display name |
| `subject.identity` | Human, device, service, agent, environment, or organization identity reference | Neutral identity steward | Independent from credentials and capabilities |
| `device.profile` | Device class, platform, ownership scope, and trusted-bootstrap assumptions | Portable-trust contract steward | Independent from observation and compliance status |
| `observation.record` | Bounded facts collected by an adapter | Source adapter | Independent from interpretation and remediation |
| `evidence.envelope` | Provenance, tool, time, artifact, hash, and collection-completeness binding | Evidence steward | Independent from transport and approval |
| `proposal.record` | Requested bounded change or disposition | Repository `0` candidate | Independent from capability and execution |
| `capability.grant` | Narrow authority to attempt a defined operation | Repository `1` or accepted authority | Independent from identity and approval evidence |
| `execution.receipt` | What operation was attempted and what occurred | Executor | Independent from canonical acceptance |
| `resulting-state.receipt` | Verified post-state and unresolved differences | Independent verifier | Independent from execution receipt |
| `canonical.disposition` | Accepted, rejected, quarantined, frozen, corrected, revoked, or superseded state | Repository `1` or accepted authority | Independent from UI display and transport status |
| `recovery.checkpoint` | Restorable state, membership, quorum, and rollback evidence | Recovery authority | Independent from ordinary canonical state |
| `correction.record` | Non-destructive amendment to prior evidence or interpretation | Original semantic owner plus authority rules | Must preserve corrected record identity |
| `revocation.record` | Withdrawal of capability, trust, acceptance, identity binding, or publication claim | Chartered revoker | Independent from deletion |
| `incident.record` | Freeze, containment, evidence preservation, restart, and recovery state | Portfolio incident command | Independent from subsystem issue tracking |
| `review.record` | Human or independent review disposition and rationale | Review authority | Independent from interface interaction |
| `publication.manifest` | Public artifact set, source commits, licenses, redactions, and rollback | Publication steward | Independent from product acceptance |

Candidate ownership is not acceptance. Exact owners must be approved and recorded without allowing the same actor to propose, execute, verify, approve, revoke, and recover a consequential operation alone.

## Universal envelope

Every portable contract should expose or bind the following conceptual fields:

```text
contract_name
contract_version
record_id
record_type
record_version
created_at
producer_identity
subject_identity
scope
source_repositories[]
source_commits[]
parent_record_ids[]
policy_refs[]
authority_refs[]
payload_digest
attachments[]
privacy_class
retention_class
freshness_domain
replay_domain
extensions{}
disposition
correction_of
revokes
supersedes
```

This is a semantic profile, not an accepted wire schema. D3 must decide canonical bytes, field representation, Unicode normalization, number handling, timestamps, digest algorithms, signatures, namespaces, optionality, extension behavior, and unsupported-state handling.

## Identity invariants

1. Repository identity is not derived solely from repository name or URL.
2. Subject identity is distinct from credentials, capabilities, accounts, and display names.
3. Device identity is distinct from hostname, IP address, Bluetooth name, serial-number display, and user account.
4. A proposal, capability, execution receipt, resulting-state receipt, and canonical disposition each have independent record identities.
5. Correction, revocation, and supersession preserve prior records rather than rewriting history.
6. A record identity cannot silently change when transported, rendered, cached, migrated, or republished.
7. Unknown or conflicting identity evidence fails closed.

## Versioning

Contracts use semantic compatibility classes rather than assuming that all schema changes are interchangeable:

- **PATCH** — clarifies documentation or adds fixtures without changing accepted meaning or wire representation;
- **MINOR** — adds optional, explicitly ignorable information under accepted extension rules;
- **MAJOR** — changes required fields, canonical bytes, identity, authority meaning, validation behavior, failure posture, or security expectations.

A consumer must reject unsupported major versions. Ignoring an unknown field is allowed only when the contract explicitly marks the extension as non-authoritative and safe to ignore. Lossy down-conversion must be explicit, evidenced, and prohibited for authority-bearing records unless separately approved.

## Canonicalization and signatures

The standard requires a future D3 profile to define:

- UTF-8 validity and Unicode normalization;
- duplicate-key rejection;
- finite numeric representation and range limits;
- timestamp precision, timezone, trusted-clock assumptions, and uncertainty;
- deterministic map and list ordering rules;
- digest and signature-reference algorithms;
- detached attachment hashing and media-type binding;
- maximum sizes and nesting;
- prohibited sensitive fields;
- signature domain separation by contract, version, role, environment, and replay domain.

Until that profile is accepted, contract examples and fixtures remain non-authoritative.

## Cross-repository edge declaration

Each edge must be documented using this table:

| Field | Requirement |
|---|---|
| Producer | One repository role that creates the semantic record |
| Consumer | One or more roles that validate or act on it |
| Contract | Exact family and supported versions |
| Preconditions | Identity, policy, freshness, authority, privacy, and dependency requirements |
| Success | What evidence proves only this edge succeeded |
| Failure | Closed failure states and reason codes |
| Correction | How prior claims are amended |
| Revocation | How downstream users learn the record is no longer valid |
| Rollback | How effects are reversed or contained |
| Fixtures | Positive, negative, stale, replay, version, identity, partial-failure, and rollback cases |
| Non-authority | Explicit statement of what transport or validation does not authorize |

## Required pairwise edges

The minimum portfolio must define and test:

1. charter → neutral contract standard;
2. contract standard → every repository-local contract declaration;
3. host adapter → Repository `0` observation admission;
4. Repository `0` proposal → Repository `1` quarantine;
5. Repository `1` capability → Repository `0` bounded execution;
6. executor → evidence and resulting-state verification;
7. evidence/temporal invariants → canonical disposition;
8. QSO-GENOMES → QuantumStateObjects;
9. QuantumStateObjects → QSO-FABRIC;
10. Fabric → kernel or conformance layer;
11. QSO-SEEKER → source and evidence pipeline;
12. QSO-DIGITALIS/Bridge → transport and disposition pipeline;
13. QSO-STUDIO/AionUi → independent review boundary;
14. QSO-PAYMENTS → separately approved financial authority;
15. publication manifest → GitHub Pages or release artifacts.

## Triple-overlap witnesses

Pairwise compatibility is insufficient when three components can interpret the same concept differently. Required triple witnesses include:

- Repository `0` + Repository `1` + portable host adapter;
- QSO-GENOMES + QuantumStateObjects + QSO-FABRIC;
- QuantumStateObjects + QSO-FABRIC + kernel/conformance layer;
- QSO-SEEKER + temporal invariants + evidence envelope;
- QSO-DIGITALIS + Bridge + Repository `1` disposition;
- QSO-STUDIO + AionUi + independent review authority;
- Repository `1` + QSO-PAYMENTS + human financial approval;
- accepted repository head + publication manifest + rendered Pages artifact.

Each triple witness must prove that identity, meaning, correction, revocation, authority, and failure states remain consistent around the complete overlap.

## Obstruction classes

A composition is blocked when any of the following exists:

- two repositories claim semantic ownership of the same record;
- no repository owns a required record or failure state;
- a producer and consumer assign different meanings to the same field;
- a transport wrapper changes identity or authority semantics;
- UI interaction is treated as approval;
- execution success is treated as canonical acceptance;
- evidence lacks source commit, tool version, completeness, or hash binding;
- clocks, freshness, or replay domains are incompatible;
- corrections or revocations do not propagate to caches, publications, or dependent records;
- rollback restores data but not authority, identity, or downstream claims;
- private data crosses a publication or retention boundary without policy;
- dependency cycles require a component to authorize itself;
- optional fields are silently required by one consumer;
- unsupported versions are accepted optimistically;
- one record identity collapses observation, interpretation, proposal, capability, execution, and acceptance;
- exact accepted versions cannot be reconstructed from provenance.

## Homology-like gluing test

The portfolio uses “homology-like” as an engineering analogy, not a claim of formal topological computation. A repository graph glues successfully only when:

1. local repository contracts are internally consistent;
2. every shared boundary has a deterministic pairwise witness;
3. every meaningful triple overlap agrees on identity and semantics;
4. traversing a contract cycle returns the same accepted meaning, authority, and revocation state;
5. corrections and rollbacks propagate around the cycle without leaving contradictory residual state;
6. no non-trivial unresolved obstruction remains hidden behind transport or UI success.

A failed cycle produces an obstruction record with the repositories, contracts, versions, fixture, expected state, observed state, owner, severity, containment, and repair candidate.

## Minimum synthetic acceptance slice

Before any production authority is considered, the portfolio should pass a synthetic, local-only slice:

1. a mock host adapter emits an observation with complete provenance;
2. Repository `0` validates it and emits a separate proposal;
3. Repository `1` quarantines the proposal and rejects stale, replayed, mismatched-device, unsupported-version, and expected-head failures;
4. a mock human approval source authorizes one narrow simulated capability;
5. a simulator emits independent execution and resulting-state receipts;
6. Repository `1` reconciles the receipts without equating execution success with acceptance;
7. a correction and revocation propagate through Studio/AionUi renderings and a mock publication manifest;
8. rollback restores the synthetic checkpoint and invalidates superseded claims;
9. all records retain exact contract versions, repository commits, artifact hashes, and independent identities.

Passing this slice demonstrates contract coherence only. It does not demonstrate device security, production autonomy, payment safety, deployment readiness, or general intelligence.

## Adoption gates

Adoption requires:

- D1 canonical charter identity;
- D2 neutral, non-operational contract stewardship;
- D3 canonical-byte and identity profile;
- D4 independent authority and recovery roots;
- D5 portfolio incident command;
- repository-by-repository reconciliation at immutable heads;
- cross-language fixtures and hostile-input tests;
- privacy, retention, security, licensing, accessibility, migration, deprecation, and rollback review;
- explicit human acceptance and a documentation-only release manifest.
