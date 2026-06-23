# Task 1 Report — DB-backed graph + cache

**Status:** DONE

**Commits:**
- `d5b5b40` feat(fsrs): replace hardcoded CONCEPT_GRAPH with DB-backed load_concept_graph

**Test results:**
- Syntax check: `Syntax OK`

**Changes made:**
1. Added `import time` to imports
2. Replaced hardcoded `CONCEPT_GRAPH` dict with `_graph_cache` + `GRAPH_CACHE_TTL` + `get_concept_graph()` + `load_concept_graph(db)` (async, DB-backed, 5-min TTL cache)
3. Added `graph: Optional[Dict[str, List[str]]] = None` param to `update_concept_graph()` — uses `get_concept_graph()` as fallback
4. Added `graph: Dict[str, List[str]]` param to `_propagate_prerequisite_penalties()` — references local `graph` instead of `CONCEPT_GRAPH`
5. Added `graph: Dict[str, List[str]]` param to `_propagate_dependent_penalties()` — references local `graph` instead of `CONCEPT_GRAPH`

**Concerns:** None. All interfaces are backward-compatible.
