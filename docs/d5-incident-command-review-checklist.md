# D5 independent review checklist

Status: **`BLOCKED_UPSTREAM_D4_AND_MISSING_INCIDENT_COMMAND_EVIDENCE`**

This checklist supports review of the [D5 portfolio incident-command packet](d5-portfolio-incident-command-decision-packet.md). It appoints no reviewer, commander, evidence custodian, recovery owner, publication authority, or closure witness and authorizes no operational action.

## Source and authority

- [ ] Confirm the exact D1–D4 dependency generations.
- [ ] Confirm every observed repository, pull request, issue, workflow, artifact, and digest.
- [ ] Confirm the proposed command model remains unselected.
- [ ] Confirm incident command cannot bootstrap its own constitutional authority.
- [ ] Confirm the suspected component cannot be the sole investigator, evidence custodian, repair approver, restorer, and closure witness.

## Scope and evidence

- [ ] Identify the affected repositories, contracts, consumers, data, devices, credentials, payments, workflows, publications, and infrastructure.
- [ ] Record explicit exclusions and the narrowest justified freeze scope.
- [ ] Verify evidence duplication, access controls, chain of custody, retention, privacy, legal hold, and contested-history preservation.
- [ ] Preserve unknown, disputed, partial, inaccessible, superseded, and withdrawn evidence states.
- [ ] Reject destructive history rewriting or silent replacement of disputed evidence.

## Lifecycle and propagation

- [ ] Trace one false alarm, unresolved hold, declared incident, partial freeze, full freeze, failed repair, failed rollback, recovery, claim withdrawal, and closure.
- [ ] Verify severity, declaration, renewal, escalation, succession, recusal, dissent, and appeal rules.
- [ ] Verify correction and revocation reach every registered consumer.
- [ ] Preserve unreachable or non-acknowledging consumers as explicit obstructions.
- [ ] Verify public claims are corrected or withdrawn through separately governed publication channels.
- [ ] Confirm rollback cannot revive revoked authority, withdrawn consent, stale credentials, invalidated claims, or superseded state.

## Recovery and closure

- [ ] Verify checkpoint ancestry, mixed-generation behavior, split-brain handling, degraded mode, and failed-rollback disposition.
- [ ] Confirm the suspected authority root cannot approve its own restoration.
- [ ] Require exact resulting-state evidence from an independent witness.
- [ ] Distinguish technical service recovery from contract repair, consumer reconciliation, legal closure, and public correction.
- [ ] Retain residual risks, failed attempts, dissent, lessons learned, follow-up owners or vacancies, and recurrence controls.
- [ ] Reject closure when any source, dependency, consumer, rollback point, publication surface, or resulting state is unknown.

## Accessibility and communication

- [ ] Provide plain-language and technical versions of consequential notices.
- [ ] Identify uncertainty, scope, affected audiences, required action, correction path, and next review point.
- [ ] Verify keyboard, screen-reader, reflow, contrast, language, and cognitive-access requirements for incident communications.
- [ ] Keep confidential, legally restricted, security-sensitive, and personal information out of public notices unless separately authorized.

## Controlled outcome

The only permitted documentation outcomes are:

- `REVIEW_EVIDENCE_COMPLETE_DECISION_UNAPPROVED`;
- `REVIEW_BLOCKED_MISSING_EVIDENCE`;
- `D5_REBIND_REQUIRED`;
- `D5_PACKET_WITHDRAWN`.

None establishes incident authority, operational readiness, certification, publication approval, or constitutional acceptance.

## FYSA-120 mapping

This checklist applies `CAT-012`, `CAT-017`, `CAT-018`, `CAT-019`, `CAT-031`, `CAT-032`, `CAT-040`, `CAT-052`, `CAT-054`, `CAT-059`, `CAT-064`, and `CAT-070`, including proposed non-authoritative subdivision **`064-F — Portfolio incident command, bounded freeze, claim withdrawal, and independently witnessed closure`**.
