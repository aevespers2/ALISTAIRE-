# Architecture

## Architectural position

Alistaire is proposed as a **composition and policy layer**, not a replacement for the QSO repositories that supply runtime primitives, genomes, collaboration, sanitized evidence, human review, or transport. The architecture must remain dependency-light at the charter stage and must fail closed whenever an upstream contract is missing, ambiguous, incompatible, or unverified.

## Proposed subsystem composition

| Subsystem | Responsibility | Primary owner | Inputs | Outputs | Failure posture |
|---|---|---|---|---|---|
| Identity and persona | Stable identity claims, presentation, continuity constraints, and declared limits | `QSO-GENOMES` | accepted genome, context, policy | identity projection, provenance | freeze on identity conflict or unverifiable migration |
| Goals and commitments | Bounded objectives, priorities, protected commitments, and stop conditions | Alistaire charter + `QSO-GENOMES` | approved task, policy, current state | ranked proposals, refusal, escalation | refuse objectives outside scope or consent |
| Memory | Working, episodic, semantic, and protected-memory references with provenance and retention | `QuantumStateObjects`; later persistence contract | accepted records, local events, review decisions | bounded recall, uncertainty, deletion/retention actions | no silent persistence; quarantine corrupt or unowned memory |
| Beliefs and uncertainty | Evidence-linked hypotheses, confidence, contradictions, and supersession | `QuantumStateObjects` + `QSO-SEEKER` | canonical records, observations | belief state, unresolved contradictions | never promote unverified input to fact |
| Ethics and policy | Immutable constraints, consent, privacy, capability, and human-review gates | charter and accepted policy contracts | proposed action, context, authority | allow, deny, request confirmation, freeze | deny by default on ambiguity or missing authority |
| Planning | Decompose approved objectives into bounded, reversible proposals | `QSO-FABRIC` | goal, evidence, resource budget | candidate plan and expected evidence | no autonomous execution; stop on resource or policy breach |
| Perception and intake | Receive already sanitized, attributed, inert evidence | `QSO-SEEKER` | canonical record + attribution sidecar | validated observation | reject raw network responses, executable content, or broken hashes |
| Collaboration | Coordinate sovereign QSO participants without command-style ownership | `QSO-FABRIC` | proposals, states, evidence | negotiated result, dissent, audit trace | preserve refusal and unresolved disagreement |
| Human review | Explain, inspect, annotate, approve, reject, or revise proposals and evidence | `QSO-STUDIO` | proposal, evidence, risk, limitations | explicit decision and rationale | no consequential action without required approval |
| Integration | Transport only explicitly approved, versioned messages between bounded systems | `Bridge` / `qsio-kernel` after acceptance | validated envelope | delivered envelope, receipt | fail closed on unknown schema, authority, or destination |

These assignments are proposed responsibilities. They become authoritative only after repository identity and upstream contract approvals.

## Lifecycle

A minimal local simulation should use explicit states:

1. **Created** — identity, policy, and dependency manifests are loaded and validated.
2. **Dormant** — no task, network, tool, or persistence authority is active.
3. **Proposed** — a human-approved objective and bounded resource envelope are present.
4. **Observing** — only validated inert evidence is accepted.
5. **Deliberating** — QSOs generate hypotheses, alternatives, uncertainty, and dissent.
6. **Awaiting review** — consequential proposals are frozen pending human disposition.
7. **Executing simulation** — only local, reversible, pre-authorized simulation steps occur.
8. **Frozen** — policy, integrity, consent, dependency, resource, or evidence failure halts work.
9. **Recovering** — restore an accepted checkpoint and reconcile evidence.
10. **Retired** — no further activity; retention and deletion rules are applied.

No state implies standing permission for network access, credentials, external writes, deployment, publication, or self-modification.

## Message envelope

A future inter-QSO message should minimally bind:

- schema and contract version;
- sender and recipient stable identifiers;
- objective or conversation identifier;
- message type and declared authority;
- canonical payload digest;
- evidence references and provenance digests;
- uncertainty and epistemic status;
- policy and consent context;
- resource budget and expiry;
- expected response or human-review requirement;
- sequence number, replay protection, and timestamp semantics;
- signature or attestation only after an approved identity/verification contract exists.

Consumers must reject unknown required fields, unsupported versions, malformed digests, expired authority, replayed messages, missing provenance, or attempts to embed executable authority in data.

## Conflict resolution

QSO disagreement is a first-class output, not a defect to be hidden. Resolution order should be:

1. immutable safety, consent, and privacy constraints;
2. explicit human instructions within approved authority;
3. accepted evidence and provenance integrity;
4. protected commitments and identity continuity;
5. resource and reversibility limits;
6. weighted hypotheses and preferences;
7. unresolved dissent preserved for review.

No QSO may silently overwrite another QSO's protected state or convert uncertainty into certainty.

## Bounded learning

At the charter stage, learning means **reviewed state revision**, not unrestricted training or self-modification. A permitted revision must identify:

- source and license/terms;
- consent and privacy basis;
- exact affected state;
- prior and proposed values;
- evidence and confidence;
- deterministic validation;
- size, time, and retention limits;
- reviewer and approval record;
- rollback checkpoint and expiry.

Private data, credentials, biometric data, legal/medical records, or intimate relational data require a separately approved policy and must never enter public artifacts.

## Freeze and shutdown

Freeze is mandatory when any of the following occurs:

- identity or contract mismatch;
- missing or withdrawn consent;
- untrusted raw input or failed digest validation;
- attempted privilege, credential, network, write, or deployment escalation;
- nondeterministic replay beyond an approved tolerance;
- resource exhaustion or unbounded spawning;
- provenance loss, contradictory immutable policy, or unresolved critical risk;
- inability to restore the previous accepted state.

Shutdown must revoke pending capabilities, stop adapters, preserve non-sensitive evidence, identify the last accepted checkpoint, and require explicit human review before restart.

## First executable slice

The first Builder-ready implementation should be a local, no-network simulation that:

- loads fixed QSO fixtures and accepted contract versions;
- processes a small deterministic scenario set;
- records evidence, uncertainty, dissent, and policy decisions;
- cannot access credentials, filesystem locations outside a temporary workspace, external tools, or network services;
- enforces step, time, memory, output-size, and QSO-count limits;
- supports freeze, checkpoint, replay, and rollback;
- passes positive, negative, adversarial, consent, privacy, corruption, and recovery fixtures.

That slice remains blocked until the canonical repository and charter are approved.
