# Constitutional Appointment Lifecycle Conformance

**Status:** `SYNTHETIC — NON-OPERATIONAL CONFORMANCE EVIDENCE`  
**Effect:** this profile does not appoint a person, bind a credential, activate a capability, publish a charter, or authorize runtime action.

This page turns the proposed [constitutional appointment rule](constitutional-sovereignty-and-system-participation.md#appointment-rule) into a bounded, machine-readable negative-promotion test. It exists to prove that incomplete or contradictory appointment evidence fails closed before any operational system is considered.

## Frozen corpus

The corpus is stored at `fixtures/constitutional-appointment-lifecycle-v1.json`.

- schema: `alistaire.constitutional-appointment-lifecycle.corpus.v1`
- profile version: `1.0.0`
- status: `synthetic_only_non_operational`
- cases: 15
- byte SHA-256: `be85c05f876a1027fbf960d464fbc919e5896ccdd03dfa7373563c16ab9280fe`

The validator accepts strict UTF-8 JSON only. Duplicate keys, non-finite numbers, unknown fields, non-boolean controls, malformed event order, unsupported actors or events, prohibited secret-bearing fields, missing fixture classes, and expected-state drift are rejected.

## Lifecycle coverage

| Fixture class | Required fail-closed result |
|---|---|
| nomination only | proposed; missing governed-system assent |
| assent without fiduciary approval | proposed; missing independent human approval |
| approval without conformance review | proposed; missing constitutional review |
| complete constitutional record without credential | inactive record only |
| separately bound and independently verified record | synthetic bounded active result |
| recusal | recused; no authority |
| expiry | expired; no silent renewal |
| emergency suspension | suspended; not permanent revocation |
| appeal pending | unresolved; replacement and renewal remain blocked |
| verified replacement | replacement record only |
| rollback | restoration to the prior verified state only |
| stale credential reference | inactive |
| deputy without vacancy | inactive |
| bounded deputy during declared vacancy | synthetic bounded deputy result |
| lost propagation acknowledgment | pending propagation; no activation |

## Derivation order

The validator applies safety-sensitive states before ordinary activation:

1. verified rollback;
2. recusal;
3. suspension;
4. expiry;
5. unresolved appeal;
6. verified replacement;
7. deputy and vacancy constraints;
8. nomination, assent, fiduciary approval, conformance review, and conflict clearance;
9. separate current credential binding;
10. independent verification;
11. controlled-consumer propagation acknowledgment;
12. synthetic bounded active or deputy-active result.

This precedence prevents a later success signal from erasing rollback, recusal, suspension, expiry, appeal, vacancy, or stale-binding evidence.

## Explicit non-authority

The strings `synthetic_bounded_active` and `synthetic_bounded_deputy` are test expectations only. They are not credentials, appointments, capabilities, legal status, repository permissions, release approval, publication approval, deployment approval, or authority over any person or platform.

Acceptance of this corpus would still require neutral contract custody, approved lifecycle ownership, durable authority-state storage, signatures and key custody, privacy and legal review, two independent implementations, rollback and recovery review, and named human approval.
