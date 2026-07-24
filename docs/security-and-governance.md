# Security, privacy, and governance

## Security objective

Alistaire must remain a bounded composition layer whose authority is explicit, revocable, observable, and no greater than the accepted authority of its dependencies. The system must fail closed when identity, consent, provenance, policy, contract, capability, or recovery evidence is missing or ambiguous.

## Protected assets

- human and QSO identity continuity;
- consent and withdrawal state;
- private, sensitive, intimate, legal, medical, biometric, and location data;
- credentials, tokens, keys, cookies, and session material;
- immutable policy and protected commitments;
- canonical records, attribution, provenance, and evidence digests;
- memory integrity, retention, deletion, and supersession records;
- capability grants, resource budgets, and approval records;
- checkpoints, rollback bundles, and incident evidence.

## Trust boundaries

| Boundary | Default posture |
|---|---|
| Human to Alistaire | authenticate intent and scope; consequential authority requires explicit current approval |
| External source to Seeker | hostile; retrieve read-only, sanitize, canonicalize, attribute, and never execute |
| Seeker to Alistaire | inert records only; verify contract versions and hashes before use |
| QSO to QSO | mutually untrusted state; schema validation, provenance, replay protection, and refusal preserved |
| Alistaire to Studio | review data and proposals, not silent execution authority |
| Alistaire to tools/Bridge | disabled until a separately approved capability grant and adapter contract exist |
| Persistence | disabled or temporary by default; explicit data classes, retention, encryption, deletion, and recovery required |
| Build and release | least privilege, exact source, pinned dependencies/actions, retained checksums and provenance |

## Consent and capacity

Consent must be informed, freely given, specific, current, revocable, and within the person's capacity and authority. Silence, prior consent, roleplay, inferred preference, or relationship framing is not current real-world authorization.

Fail closed on:

- missing, ambiguous, expired, withdrawn, coerced, or unverifiable consent;
- identity or scope mismatch;
- impairment or inability to consent;
- unsafe power imbalance;
- attempts to fabricate or infer consent;
- requests involving another person without their authority.

A freeze must revoke pending actions, preserve non-sensitive evidence, and require fresh human review. There is no automatic unlock.

## Capability model

Capabilities are deny-by-default and should be represented as short-lived grants binding:

- principal and authenticated identity;
- exact action class and target;
- allowed data and purpose;
- time, step, size, rate, and cost limits;
- network, filesystem, process, and repository boundaries;
- approval and consent references;
- audit and evidence requirements;
- expiry and revocation behavior;
- rollback or compensation plan.

No component may discover credentials, broaden a grant, delegate authority, or convert a proposal into execution without an accepted contract.

## Learning and memory policy

At the charter stage, the permitted model is reviewed local state revision. No background training, self-rewriting, autonomous model updates, or unbounded memory growth is authorized.

Every retained item needs:

- source and provenance;
- data classification;
- purpose and legal/consent basis;
- owner and access policy;
- confidence and supersession relation;
- retention period and deletion behavior;
- integrity digest;
- review and rollback record.

Sensitive information must not appear in public repositories, logs, fixtures, workflow artifacts, screenshots, issue bodies, or generated Pages content.

## Threat classes

The review must cover at least:

- prompt and data injection;
- Unicode concealment and parser differentials;
- malicious or executable content;
- dependency and action compromise;
- credential leakage or confused-deputy behavior;
- unauthorized network, filesystem, subprocess, repository, deployment, or payment authority;
- memory poisoning, provenance stripping, identity drift, and belief escalation;
- replay, substitution, downgrade, and contract-confusion attacks;
- privacy leakage through logs, caches, telemetry, artifacts, or summaries;
- coercion, consent bypass, manipulation, and unsafe relational dynamics;
- resource exhaustion, uncontrolled spawning, and persistence growth;
- shutdown, freeze, rollback, or human-review bypass;
- false claims of consciousness, certainty, security, compliance, or production readiness.

## Human governance

Human review is required for:

- canonical repository and package identity;
- policy or immutable-commitment changes;
- new data classes or persistence;
- external tools, network access, credentials, writes, publication, deployment, or spending;
- training, self-modification, or model replacement;
- safety, privacy, consent, or evidence exceptions;
- release promotion and rollback completion.

Review decisions must identify the exact commit and artifacts, evidence considered, unresolved risks, expiry, rollback, and reviewer authority.

## Incident response

1. **Freeze** all relevant components and revoke capability grants.
2. **Contain** network, credentials, adapters, schedules, and writes.
3. **Preserve** minimal non-sensitive evidence with hashes and timestamps.
4. **Classify** affected identities, data, contracts, repositories, and external systems.
5. **Restore** the last accepted checkpoint in an isolated environment.
6. **Reproduce** the failure with bounded fixtures where safe.
7. **Repair** through a reviewed branch without destroying failed-candidate evidence.
8. **Validate** deterministic, negative, security, privacy, consent, and rollback tests.
9. **Approve** restart explicitly; never automatically resume.
10. **Document** residual risk, notification obligations, retention, and follow-up controls.

## Release-blocking conditions

A candidate cannot be approved while any of these remains true:

- competing canonical repository identities;
- ambiguous QSO ownership or contract versions;
- unsupported capability or AGI claims;
- missing consent, privacy, threat, or misuse review;
- unbounded learning, persistence, tools, network, resources, or spawning;
- missing exact-head validation, checksums, provenance, evidence retention, or rollback;
- inability to reproduce and independently review the documentation or fixtures.
