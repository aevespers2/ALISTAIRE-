# Developer and reviewer onboarding

## Current contribution boundary

Only documentation, inventory, provenance, contract proposals, validation fixtures, and evidence-preservation work are eligible while P0 is blocked. Do not add runtime code, autonomous learning, network access, credentials, external-tool execution, persistence, deployment, or capability claims.

## Local documentation environment

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Repository review order

1. Read `taskchain.md` for the active objective and stop conditions.
2. Read `release.md` for acceptance gates and prohibited release claims.
3. Read `punchlist.md` for evidence requirements.
4. Review the consolidation decision and confirm whether the work depends on unresolved P0 approval.
5. Check upstream repositories before assigning ownership or claiming a contract exists.
6. Classify each statement as observed, implemented, verified, proposed, hypothetical, or prohibited.
7. Build the documentation strictly from a clean environment.
8. Record exact commits, commands, outputs, limitations, and rollback.

## Documentation rules

- Do not convert an empty scaffold filename into a capability claim.
- Keep present behavior separate from proposed architecture.
- Link repository ownership explicitly instead of duplicating upstream design.
- Use diagrams to clarify boundaries, not to imply implementation.
- Mark examples as conceptual unless validated against an accepted schema.
- Never include credentials, private data, personal records, or sensitive incident details.
- Use absolute repository/commit identities in evidence records.
- Preserve uncertainty and disagreements rather than smoothing them into certainty.

## Naming and terminology

- On first public use, write **A.L.I.S.T.A.I.R.E. (Adaptive Learning & Intelligence System for Trustworthy Autonomous Inference, Reasoning, and Evolution)**.
- Use **Alistaire** afterward for the project display name; use exact repository names for source, workflow, provenance, and migration records.
- Keep `A.L.I.S.T.A.I.R.E.`, `Alistaire`, `aevespers2/ALISTAIRE-`, `aevespers2/Alistaire-agi`, and the proposed `alistaire-qso` package identity distinct.
- Treat “autonomous” as bounded internal inference under accepted policies and review. It never grants network, credential, device, payment, release, publication, deployment, or self-modification authority.
- Do not shorten the project to “AI” when the abbreviation could blur identity, evidence status, or authority.
- Give acronyms, diagrams, status codes, and symbolic notation a plain-language equivalent.
- Preserve superseded names and meanings with provenance, rationale, migration effects, and rollback rather than silently rewriting history.
- Follow the [name and identity guide](name-and-identity.md) for public wording and rename change control.

## Proposed documentation structure

The canonical repository should maintain a small authoritative set:

- project and product overview;
- name, identity, terminology, and public style guidance;
- repository-consolidation decision and migration manifest;
- architecture and responsibility matrix;
- contracts and compatibility references;
- lifecycle, learning, memory, privacy, consent, freeze, shutdown, and rollback policies;
- evaluation and adversarial-fixture specification;
- developer/reviewer onboarding;
- operations and incident response;
- release gates, changelog, and provenance.

The large placeholder taxonomy in `Alistaire-agi` should become a reviewed backlog, not hundreds of empty published pages.

## Change workflow

1. Create a branch from the exact current canonical candidate head.
2. State the documentation objective and implementation non-goals.
3. Modify the smallest coherent set of files.
4. Run `mkdocs build --strict`.
5. Inspect links, navigation, headings, tables, code blocks, and Mermaid source.
6. Scan for secrets, sensitive data, hidden controls, unsupported claims, and contradictory authority.
7. Reconcile `taskchain.md`, `release.md`, `punchlist.md`, and `changelog.md` when status changes.
8. Open a draft pull request with exact-head evidence and unresolved decisions.
9. Rerun checks after every material review change.
10. Merge or release only after explicit approval.

## Evidence record template

```markdown
### YYYY-MM-DD — <task>

- Repositories and commits:
- Branch / pull request:
- Environment and tool versions:
- Commands:
- Result: PASS | FAIL | UNKNOWN
- Files or artifacts:
- SHA-256 digests:
- Security/privacy review:
- Limitations and residual risks:
- Reviewer and disposition:
- Rollback procedure:
- Follow-up:
```

## Review checklist

### Scope

- Does the change remain documentation-only?
- Does it preserve the blocked canonical-repository gate?
- Are implemented and proposed capabilities clearly separated?
- Does it avoid duplicating upstream repository ownership?

### Architecture

- Are inputs, outputs, state, authority, failure modes, and owners explicit?
- Are trust boundaries, consent, privacy, evidence, freeze, and rollback shown?
- Are unknown or pending contracts marked as blocked?

### Naming and accessibility

- Is the acronym expanded correctly on first use?
- Are project, repository, and package identities kept distinct?
- Is “autonomous” bounded rather than presented as operational permission?
- Do diagrams and status vocabulary have equivalent prose?
- Would a new contributor understand how a rename is corrected, migrated, and rolled back?

### Quality

- Does `mkdocs build --strict` pass from a clean environment?
- Are links, navigation, terminology, tables, examples, and diagrams coherent?
- Are public claims supported by immutable evidence?

### Security and governance

- Are sensitive data and secrets absent?
- Are capability grants explicit and deny-by-default?
- Are consent and human-review requirements preserved?
- Are incident response and rollback actionable?

## Stop conditions

Stop and request architectural disposition when a change requires:

- choosing the canonical repository or package identity;
- declaring a final product mode;
- assigning an overlapping repository responsibility;
- approving learning sources, persistence, credentials, network, tools, writes, or deployment;
- changing consent, privacy, immutable policy, freeze, or shutdown behavior;
- claiming AGI, consciousness, sentience, security, compliance, or production readiness;
- starting runtime implementation before P0-P3 are accepted.
