# Graphe Topologique FSRS — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace hardcoded `CONCEPT_GRAPH` with DB-backed dependency graph and add topological sorting to FSRS scheduler.

**Architecture:** Add async `load_concept_graph(db)` with in-memory cache (TTL 300s) to `fsrs_graph.py`. Add Kahn topological sort to `fsrs_scheduler.py`. Update `evaluate.py` and `reconciliation_queue.py` to load graph before `update_concept_graph`.

**Tech Stack:** FastAPI, PostgreSQL, SQLAlchemy async, Python 3.12

## Global Constraints
- `ANY(:array)` not `IN :tuple` (asyncpg bug)
- `CAST(:emb AS vector)` not `::vector`
- No hardcoded secrets: use `get_settings().X`
- Queries via `text(...)` or model, never raw SQL concat
- Cache with TTL to avoid repeated DB calls

---

### Task 1: Refactor `fsrs_graph.py` — DB-backed graph + cache

**Files:**
- Modify: `khawarizmi-backend/services/fsrs_graph.py`

**Interfaces:**
- Produces: `load_concept_graph(db)` → `Dict[str, List[str]]`, `get_concept_graph()` → `Dict[str, List[str]]`, `update_concept_graph(..., graph=None)`

- [ ] **Step 1: Delete `CONCEPT_GRAPH` dict (lines 18-31). Add cache + helper functions**

After line 17 (`default_scheduler = Scheduler()`), add:
- `_graph_cache: Dict[str, Any] = {"data": {}, "timestamp": 0.0}`
- `GRAPH_CACHE_TTL = 300`
- `get_concept_graph()` → returns cache data or empty dict
- `async def load_concept_graph(db) -> Dict[str, List[str]]`: queries `concept_prerequisites`, builds `{concept_id: [prereq_ids]}`, updates cache. TTL check before DB call.

- [ ] **Step 2: Update `update_concept_graph` signature** — add `graph: Optional[Dict[str, List[str]]] = None` parameter. Use `graph if graph is not None else get_concept_graph()`. Pass `graph` to both propagation functions.

- [ ] **Step 3: Update `_propagate_prerequisite_penalties`** — add `graph: Dict[str, List[str]]` parameter, reference `graph` instead of module-level `CONCEPT_GRAPH`.

- [ ] **Step 4: Update `_propagate_dependent_penalties`** — add `graph: Dict[str, List[str]]` parameter, iterate `graph.items()` instead of `CONCEPT_GRAPH.items()`.

- [ ] **Step 5: Verify syntax** — `cd khawarizmi-backend && python -c "import ast; ast.parse(open('services/fsrs_graph.py').read()); print('Syntax OK')"`

- [ ] **Step 6: Commit** — `git add khawarizmi-backend/services/fsrs_graph.py && git commit -m "feat(fsrs): replace hardcoded CONCEPT_GRAPH with DB-backed load_concept_graph"`

---

### Task 2: Add topological sort to `fsrs_scheduler.py`

**Files:**
- Modify: `khawarizmi-backend/services/fsrs_scheduler.py`

- [ ] **Step 1: Add `from collections import deque` import. Add `_topological_sort(concept_ids, graph)` function** — Kahn algorithm as specified in the design doc.

- [ ] **Step 2: Modify `get_due_concepts`** — after building `due_concepts` list, call `await load_concept_graph(db)`. If graph non-empty, apply `_topological_sort()`. Sort `due_concepts` by (topo_order, stability). Wrap in try/except — fallback to default order on error.

- [ ] **Step 3: Verify syntax** — `cd khawarizmi-backend && python -c "import ast; ast.parse(open('services/fsrs_scheduler.py').read()); print('Syntax OK')"`

- [ ] **Step 4: Commit** — `git add khawarizmi-backend/services/fsrs_scheduler.py && git commit -m "feat(fsrs): add topological sort to get_due_concepts"`

---

### Task 3: Update `routes/evaluate.py` — load graph before FSRS update

**Files:**
- Modify: `khawarizmi-backend/routes/evaluate.py` (line ~174)

- [ ] **Step 1: Before `updates = update_concept_graph(`, add:**
```python
from services.fsrs_graph import load_concept_graph
concept_graph = await load_concept_graph(db)
```
Pass `graph=concept_graph` to `update_concept_graph`.

- [ ] **Step 2: Commit** — `git add khawarizmi-backend/routes/evaluate.py && git commit -m "feat(evaluate): load concept graph from DB before FSRS update"`

---

### Task 4: Update `services/reconciliation_queue.py` — same pattern

**Files:**
- Modify: `khawarizmi-backend/services/reconciliation_queue.py` (line ~111)

- [ ] **Step 1: Same change as evaluate.py** — load graph before `update_concept_graph`, pass `graph=`.

- [ ] **Step 2: Commit** — `git add khawarizmi-backend/services/reconciliation_queue.py && git commit -m "feat(reconciliation): load concept graph from DB before FSRS update"`

---

### Task 5: Write tests

**Files:**
- Create: `khawarizmi-backend/tests/test_topological_sort.py`

- [ ] **Step 1: Create test file with unit tests for `_topological_sort`**:
  - `test_linear_chain`: A→B→C — assert ordering
  - `test_star_graph`: A→B, A→C, A→D — A first
  - `test_empty_graph`: no deps — all returned
  - `test_single_concept`: single element
  - `test_diamond_graph`: A→B, A→C, B→D, C→D — A first, D last
  - `test_cycle_handling`: A→B→A — cycle doesn't crash, returns all

- [ ] **Step 2: Run tests** — `cd khawarizmi-backend && python -m pytest tests/test_topological_sort.py -v`
Expected: 6/6 passed

- [ ] **Step 3: Add integration test in `test_fsrs.py`** — test that `load_concept_graph` returns correct structure (needs DB fixture). Mark with `@pytest.mark.asyncio`.

- [ ] **Step 4: Commit** — `git add tests/ && git commit -m "test(fsrs): add topological sort and concept graph tests"`

---

### Verification

- [ ] Run all existing tests: `cd khawarizmi-backend && python -m pytest tests/ -v`
Expected: 13/13 passed (no regressions)
- [ ] Run the app: verify import chain works
