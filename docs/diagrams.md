# Architecture diagrams

These diagrams describe the proposed charter boundary. They do not claim that the components or integrations are implemented or verified.

## Portfolio composition

```mermaid
flowchart TB
    H[Human researcher / reviewer]
    S[QSO-STUDIO\ninspection and approval]
    A[Alistaire\ncomposition and policy]
    G[QSO-GENOMES\nidentity and immutable traits]
    Q[QuantumStateObjects\nruntime primitives and lifecycle]
    F[QSO-FABRIC\ncollaboration and bounded experiments]
    K[QSO-SEEKER\nhostile-input boundary]
    B[Bridge / qsio-kernel\napproved transport]
    E[(Evidence and provenance)]

    H --> S
    S -->|approved objective / decision| A
    A --> G
    A --> Q
    A --> F
    K -->|validated inert records| A
    A -. proposed envelopes .-> B
    G --> E
    Q --> E
    F --> E
    K --> E
    A --> E
    E --> S
```

## Authority and trust boundaries

```mermaid
flowchart LR
    X[External source\nhostile] --> R[Read-only retrieval]
    R --> Z[Sanitization and canonicalization]
    Z -->|hash-verified inert artifact| A[Alistaire local simulation]
    U[Human authority] -->|explicit scoped approval| A
    A --> P[Proposal and evidence]
    P --> V[Human review surface]
    V -->|approve / reject / revise| A
    A -. disabled by default .-> T[Network, tools, writes, deployment]

    classDef boundary stroke-width:3px,stroke-dasharray:5 5;
    class R,Z,A,V boundary;
```

## Lifecycle and freeze path

```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> Dormant: contracts and policy valid
    Created --> Frozen: validation failure
    Dormant --> Proposed: approved bounded objective
    Proposed --> Observing
    Observing --> Deliberating: accepted evidence
    Observing --> Frozen: hostile/raw/broken evidence
    Deliberating --> AwaitingReview: consequential proposal
    Deliberating --> Frozen: policy, consent, integrity, or resource failure
    AwaitingReview --> Simulation: explicit approval
    AwaitingReview --> Dormant: rejected or withdrawn
    Simulation --> Dormant: completed and checkpointed
    Simulation --> Frozen: boundary violation or nondeterminism
    Frozen --> Recovering: human-authorized recovery
    Recovering --> Dormant: accepted checkpoint restored
    Recovering --> Retired: recovery cannot be validated
    Dormant --> Retired: explicit retirement
    Retired --> [*]
```

## Evidence flow

```mermaid
sequenceDiagram
    participant Human
    participant Studio
    participant Alistaire
    participant Seeker
    participant QSOs
    participant Evidence

    Human->>Studio: Define bounded objective and limits
    Studio->>Alistaire: Approved objective envelope
    Alistaire->>Seeker: Request already-authorized evidence class
    Seeker-->>Alistaire: Canonical record + attribution + digests
    Alistaire->>Alistaire: Verify contract, hashes, consent, policy
    Alistaire->>QSOs: Inert observations and resource budget
    QSOs-->>Alistaire: Hypotheses, dissent, uncertainty, proposals
    Alistaire->>Evidence: Append provenance and decision trace
    Alistaire-->>Studio: Proposal, risks, limits, rollback
    Studio-->>Human: Review package
    Human->>Studio: Approve, reject, or revise
    Studio->>Evidence: Record explicit disposition
```

## Repository consolidation

```mermaid
flowchart TB
    A1[ALISTAIRE-\nsubstantive charter history]
    A2[Alistaire-agi\npackage-name proposal + empty topic scaffold]
    I[Cross-repository inventory and provenance manifest]
    D{Explicit canonical repository approval}
    C[Canonical repository\ncharter, Pages, release authority]
    N[Non-canonical repository\nredirect, archive, or approved distinct role]
    R[Rollback record]

    A1 --> I
    A2 --> I
    I --> D
    D --> C
    D --> N
    C --> R
    N --> R
```

## Rollback

```mermaid
flowchart LR
    F[Failure or unsafe ambiguity] --> L[Freeze and revoke pending capabilities]
    L --> P[Preserve minimal non-sensitive evidence]
    P --> C[Identify last accepted checkpoint]
    C --> I[Restore in isolated environment]
    I --> V[Replay validation and adversarial fixtures]
    V -->|pass + human approval| D[Dormant reviewed state]
    V -->|fail| W[Withdraw candidate and retain evidence]
```
