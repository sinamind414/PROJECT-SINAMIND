# Task 2: Add topological sort to `fsrs_scheduler.py`

**Goal:** Add Kahn topological sort algorithm + apply it in `get_due_concepts()` so prerequisite concepts are returned before dependents.

## Consumes (from Task 1)
- `load_concept_graph(db)` — async, caches, returns `Dict[str, List[str]]`
- Already imported via `from services.fsrs_graph import load_concept_graph`

## Files
- Modify: `khawarizmi-backend/services/fsrs_scheduler.py`

## Steps

### Step 1: Add `from collections import deque` import

Add after line 6 (after `from datetime import datetime, timezone, timedelta`).

### Step 2: Add `_topological_sort` function

Add after `logger = logging.getLogger("khawarizmi.fsrs_scheduler")` (line 14):

```python
def _topological_sort(concept_ids: List[str], graph: Dict[str, List[str]]) -> List[str]:
    """Kahn topological sort: prerequisites before dependents."""
    in_degree = {c: 0 for c in concept_ids}
    for deps in graph.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1
    queue = deque([c for c in in_degree if in_degree[c] == 0])
    sorted_list = []
    while queue:
        node = queue.popleft()
        sorted_list.append(node)
        for dep in graph.get(node, []):
            if dep in in_degree:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
    remaining = [c for c in concept_ids if c not in sorted_list]
    return sorted_list + remaining
```

### Step 3: Modify `get_due_concepts` — add topological sort

After building `due_concepts` list (after the for loop that appends rows) and before the `logger.info` line, add:

```python
    # Topological sort: prerequisites before dependents
    if due_concepts:
        try:
            from services.fsrs_graph import load_concept_graph
            graph = await load_concept_graph(db)
            if graph:
                ordered_ids = _topological_sort([c["concept_id"] for c in due_concepts], graph)
                id_order = {cid: i for i, cid in enumerate(ordered_ids)}
                due_concepts.sort(key=lambda c: (id_order.get(c["concept_id"], 999), c["stability"]))
        except Exception as e:
            logger.warning(f"Topological sort failed, falling back to default order: {e}")
```

### Step 4: Verify syntax

```bash
cd khawarizmi-backend && python -c "import ast; ast.parse(open('services/fsrs_scheduler.py').read()); print('Syntax OK')"
```

### Step 5: Commit

```bash
git add khawarizmi-backend/services/fsrs_scheduler.py
git commit -m "feat(fsrs): add topological sort to get_due_concepts"
```
