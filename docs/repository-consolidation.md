# Repository consolidation decision

## Decision required

Two repositories currently present the Alistaire product identity:

- `aevespers2/ALISTAIRE-`
- `aevespers2/Alistaire-agi`

This document records the observed evidence, decision criteria, migration options, and a recommendation. It does not itself approve the canonical repository.

## Observed inventory

### `aevespers2/ALISTAIRE-`

Observed substantive coordination content:

- product-level directive and non-goals in `taskchain.md`;
- P0-P6 roadmap and approval gates;
- documentation-only release gates in `release.md`;
- repository-consolidation and charter punch list;
- changelog entries describing the product decision and duplicate-identity hold;
- preserved commit history for the initial charter direction.

Observed gaps:

- no polished README or Pages site before this candidate;
- no approved canonical repository decision;
- no runtime, tests, package manifest, schemas, dependency lock, security evidence, or release bundle.

### `aevespers2/Alistaire-agi`

Observed substantive content:

- a README naming the proposed package `alistaire-qso`;
- duplicate-identity task chain, release plan, and changelog created after the repository conflict was identified.

Observed scaffold:

- approximately 140 documentation paths were created in one initialization commit across AI, API, architecture, developer, diagrams, modules, protocols, QSO, reference, research, standards, and tutorial categories;
- the initialization commit shows no substantive patches for those files;
- sampled `docs/index.md` is empty;
- no runtime, tests, package manifest, schemas, dependency lock, CI evidence, or release bundle is established.

The scaffold is useful as a topic inventory, but empty paths are not architecture or capability evidence.

## Decision criteria

The canonical repository should maximize:

1. continuity with the first approved product directive;
2. substantive evidence over placeholder volume;
3. preserved history and attribution;
4. unambiguous package and release identity;
5. minimal disruption to open QSO work;
6. a clean Pages and reviewer experience;
7. clear separation from upstream implementation repositories;
8. reversible migration and a durable redirect/archive path.

## Options

### Option A — `ALISTAIRE-` is canonical

**Advantages**

- preserves the established product directive and release-control history;
- requires migrating only the useful package name and selected topic taxonomy;
- avoids presenting the placeholder scaffold as a completed design;
- keeps the documentation candidate on the repository with the strongest evidence trail.

**Required actions**

- approve a final repository name, preferably without the trailing hyphen;
- approve `Alistaire` as display name and decide whether `alistaire-qso` is the package identifier;
- inventory the placeholder scaffold and migrate only approved topics as issues or a documentation backlog;
- replace `Alistaire-agi` with a prominent redirect/read-only archive notice or assign a narrowly non-overlapping role;
- preserve commit links and a migration manifest.

### Option B — `Alistaire-agi` is canonical

**Advantages**

- cleaner repository name and an existing proposed package identifier;
- broad topic scaffold may serve as a long-term documentation taxonomy.

**Costs and risks**

- the substantive charter and release-control history must be migrated from `ALISTAIRE-`;
- the empty scaffold must be pruned or clearly marked to avoid unsupported completeness claims;
- provenance and issue/commit continuity are more complex;
- both repositories require coordinated notices to avoid parallel authority.

### Option C — split responsibilities

Example: one repository owns the product charter and another owns documentation or a future application.

This is **not recommended now** because neither repository contains an accepted runtime or a sufficiently distinct implementation responsibility. A split would preserve the current ambiguity and create two release identities before contracts exist.

## Recommendation

**Recommend Option A:** use `aevespers2/ALISTAIRE-` as the canonical charter history, then rename or migrate it to a clean final repository name when approved. Preserve `alistaire-qso` as a proposed package identifier rather than treating the placeholder repository as the package authority.

This recommendation is based on evidence density and provenance, not repository-name preference. It remains blocked until explicitly approved.

## Proposed migration map

| Source | Destination or disposition | Rationale |
|---|---|---|
| `ALISTAIRE-/taskchain.md` | retain as canonical coordination record | substantive first product directive |
| `ALISTAIRE-/release.md` | retain and evolve | evidence-bounded release controls |
| `ALISTAIRE-/punchlist.md` | retain and reconcile | migration and charter evidence checklist |
| `ALISTAIRE-/changelog.md` | retain | product and scope-conflict history |
| `Alistaire-agi/README.md` | migrate package-name proposal and repository link | only concise product metadata there |
| `Alistaire-agi/docs/**` empty paths | convert to backlog inventory; do not bulk-copy as completed pages | topic taxonomy without content |
| `Alistaire-agi/taskchain.md`, `release.md`, `changelog.md` | preserve by commit link and summarize in migration manifest | duplicate coordination documents created after conflict |
| non-canonical repository | redirect/read-only archive or narrowly approved distinct role | prevent competing authority |

## Approval record template

Record the following in an immutable commit or reviewed issue:

- canonical repository and final repository name;
- display name and package identifier;
- canonical documentation and release authority;
- non-canonical repository disposition;
- migration paths and excluded placeholder paths;
- attribution and commit-history preservation method;
- license and public-notice decision;
- rollback procedure;
- approver and approval date.

Until this record exists, P0 remains `BLOCKED` and no runtime or package release is authorized.
