# Spec: Graph-Based Competence Model

**Status:** Proposal — requires team review before implementation.
**Author:** Auto-generated from deep-research findings + plan Phase 6.
**Affects:** `core/models.py`, `core/competence_store.py`, `qa/competence_updates.py`

---

## Problem

The current competence model is a flat dictionary of concept → score. It lacks:
1. **Prerequisite relationships** — no way to express that `async_programming` depends on `functions` and `error_handling`.
2. **Evidence-based scoring** — scores are updated by additive deltas, with no time decay or audit trail weighting.
3. **Semantic concept resolution** — when the gate encounters a new concept name, there's no structure for determining if it maps to an existing node.

## Proposed Changes

### 1. Prerequisite Edges in YAML

Add an optional `prerequisites` key to each concept in `competence_model.yaml`:

```yaml
concepts:
  functions:
    score: 0.7
    notes: []
    evidence: [...]
    prerequisites: [variables_and_types, control_flow]
  error_handling:
    score: 0.4
    notes: []
    evidence: [...]
    prerequisites: [functions]
```

**Backward compatibility:** Models without `prerequisites` keys load with empty prerequisite lists. No migration script needed — the field is purely additive.

### 2. NetworkX DiGraph for Prerequisite Reasoning

Build a `networkx.DiGraph` from the competence model on load. Edges run from prerequisite → dependent (e.g., `functions → error_handling`).

Use cases:
- **Ancestor lookup** — `nx.ancestors(G, "async_programming")` → `{functions, error_handling, variables_and_types, control_flow}`
- **Learning frontier** — concepts where all prerequisites score ≥ threshold but the concept itself scores low
- **Weak prerequisite detection** — if a concept scores well but a prerequisite doesn't, flag the gap
- **Relevant subgraph extraction** — for gate prompts, extract only the concepts and edges relevant to the change proposal (token-efficient)

### 3. Evidence-Based Scoring with Time Decay

Replace additive `delta` scoring with:

```python
def compute_score(evidence: list[CompetenceEvidence], half_life_days: float = 30.0) -> float:
    if not evidence:
        return 0.5  # prior
    now = datetime.now(UTC)
    weighted_sum = 0.0
    weight_total = 0.0
    for ev in evidence:
        age_days = (now - parse_iso(ev.timestamp)).total_seconds() / 86400
        weight = math.exp(-0.693 * age_days / half_life_days)
        outcome_value = OUTCOME_VALUES[ev.outcome]
        weighted_sum += weight * outcome_value
        weight_total += weight
    return weighted_sum / weight_total if weight_total > 0 else 0.5
```

**Outcome values:**
| Outcome | Value |
|---------|-------|
| `pass_first_try` | 1.0 |
| `pass_after_2` | 0.7 |
| `pass_after_3` | 0.5 |
| `fail_limit_reached` | 0.1 |
| `self_assessment` | mapped from 1-5 slider |

**Half-life:** 30 days default. Recent evidence dominates; old evidence fades.

### 4. LLM-Assisted Concept Matching (Post-MVP)

When the gate identifies a concept not in the model:
1. Exact match → use existing node
2. Normalized match (lowercase + underscore) → use existing node
3. LLM query: "Is concept X semantically equivalent to any of [existing concepts]?" → map or create
4. If creating: LLM suggests prerequisite edges to existing concepts

This is deferred until the basic graph model is validated.

## Data Model Changes

### `CompetenceEntry` additions

```python
@dataclass(slots=True)
class CompetenceEntry:
    score: float
    notes: list[str] = field(default_factory=list)
    evidence: list[CompetenceEvidence] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)  # NEW
```

### New helper: `build_concept_graph`

```python
def build_concept_graph(model: CompetenceModel) -> nx.DiGraph:
    G = nx.DiGraph()
    for name, entry in model.concepts.items():
        G.add_node(name, score=entry.score, category=...)
        for prereq in entry.prerequisites:
            G.add_edge(prereq, name)
    return G
```

### Score computation changes

`competence_store.update_competence_entry` currently applies `delta`:
```python
entry.score = min(1.0, max(0.0, round(entry.score + delta, 2)))
```

Proposed: Remove delta-based scoring. Instead:
- Always append evidence
- Compute `entry.score` on read via `compute_score(entry.evidence)`
- The `score` field in YAML becomes a cached snapshot (updated on write)

## Migration Path

1. Existing models load without `prerequisites` — empty list default
2. Running `vibecheck cm init` creates a model with prerequisites from the taxonomy
3. The `compute_score` function is a pure addition — existing evidence lists work unchanged
4. The delta-based `update_competence_entry` is replaced, but the append-evidence pattern already exists in `competence_updates.py`

## Files Modified (When Approved)

| File | Change |
|------|--------|
| `core/models.py` | Add `prerequisites` field to `CompetenceEntry` |
| `core/competence_store.py` | Add `build_concept_graph()`, modify score computation |
| `qa/competence_updates.py` | Replace delta with evidence-only appends |
| `pyproject.toml` | Promote `networkx` from optional to core dependency |

## Open Questions

1. Should the half-life be configurable per-concept or global?
2. Should prerequisite edges be mutable via the QA loop, or only via explicit user action?
3. Should we persist the computed score in YAML (current approach) or compute purely on read?

## Decision Required

This spec proposes changes to the core scoring mechanism. Implementation should not proceed until the team has reviewed and approved the approach. The `networkx` dependency is already available as an optional extra (`pip install 'vibecheck[graph]'`) for experimentation.
