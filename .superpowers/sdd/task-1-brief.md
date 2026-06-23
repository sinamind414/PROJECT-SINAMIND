# Task 1: Refactor `fsrs_graph.py` — DB-backed graph + cache

**Goal:** Replace the hardcoded `CONCEPT_GRAPH` dict with an async DB-backed loader that queries `concept_prerequisites`, caches results in-memory with 5-minute TTL.

## Files
- Modify: `khawarizmi-backend/services/fsrs_graph.py`

## Produces (interfaces later tasks rely on)
- `load_concept_graph(db: AsyncSession) -> Dict[str, List[str]]` — async, caches
- `get_concept_graph() -> Dict[str, List[str]]` — sync cache reader
- `update_concept_graph(..., graph: Optional[Dict[str, List[str]]] = None)` — updated signature

## Steps

### Step 1: Add cache + helpers after `default_scheduler = Scheduler()` (line ~17)

Delete lines 18-31 (the `CONCEPT_GRAPH` dict). Add:

```python
import time

_graph_cache: Dict[str, Any] = {"data": {}, "timestamp": 0.0}
GRAPH_CACHE_TTL = 300  # 5 minutes

def get_concept_graph() -> Dict[str, List[str]]:
    return _graph_cache["data"]

async def load_concept_graph(db) -> Dict[str, List[str]]:
    now = time.time()
    if now - _graph_cache["timestamp"] < GRAPH_CACHE_TTL and _graph_cache["data"]:
        return _graph_cache["data"]
    from sqlalchemy import text
    res = await db.execute(text("""
        SELECT concept_id, prerequisite_id
        FROM concept_prerequisites
        ORDER BY concept_id
    """))
    rows = res.fetchall()
    graph: Dict[str, List[str]] = {}
    for concept_id, prereq_id in rows:
        graph.setdefault(concept_id, []).append(prereq_id)
    _graph_cache["data"] = graph
    _graph_cache["timestamp"] = now
    logger.info(f"Loaded {len(graph)} concept dependencies from DB")
    return graph
```

Note: The existing imports already have `Dict`, `List`, `Any` from `typing`. `time` needs to be added.

### Step 2: Update `update_concept_graph` signature

Add `graph: Optional[Dict[str, List[str]]] = None` parameter.
At the end (before return), use `active_graph = graph if graph is not None else get_concept_graph()` and pass `active_graph` to both propagation functions.

### Step 3: Update `_propagate_prerequisite_penalties`

Add `graph: Dict[str, List[str]]` param. Replace `CONCEPT_GRAPH` references with `graph`.

### Step 4: Update `_propagate_dependent_penalties`

Add `graph: Dict[str, List[str]]` param. Replace `CONCEPT_GRAPH` references with `graph`.

### Step 5: Verify

```bash
cd khawarizmi-backend && python -c "import ast; ast.parse(open('services/fsrs_graph.py').read()); print('Syntax OK')"
```

### Step 6: Commit

```bash
git add khawarizmi-backend/services/fsrs_graph.py
git commit -m "feat(fsrs): replace hardcoded CONCEPT_GRAPH with DB-backed load_concept_graph"
```

## Constraints
- `ANY(:array)` not `IN :tuple` (already just SELECT, fine)
- No secrets in code
- Keep existing function signatures compatible (add optional params)
