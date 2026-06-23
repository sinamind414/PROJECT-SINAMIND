# Task 4: Update `services/reconciliation_queue.py` — load graph before FSRS update

**Goal:** Same change as Task 3 — load concept dependency graph from DB before calling `update_concept_graph`.

## Consumes (from Task 1)
- `load_concept_graph(db)` — async, returns `Dict[str, List[str]]`
- `update_concept_graph(..., graph=graph)` — accepts optional graph

## Files
- Modify: `khawarizmi-backend/services/reconciliation_queue.py` (around line 111)

## Change

Before the `updates = update_concept_graph(` call (currently around line 111-119), insert:

```python
            # Charger le graphe de dépendances
            from services.fsrs_graph import load_concept_graph
            concept_graph = await load_concept_graph(db)
```

And in the `update_concept_graph(` call, add `graph=concept_graph` to the keyword arguments.

So the existing:
```python
            updates = update_concept_graph(
                user_id=int(student_id),
                ...
                user_fsrs_config=user_fsrs_config
            )
```

Becomes:
```python
            # Charger le graphe de dépendances
            from services.fsrs_graph import load_concept_graph
            concept_graph = await load_concept_graph(db)

            updates = update_concept_graph(
                user_id=int(student_id),
                ...
                user_fsrs_config=user_fsrs_config,
                graph=concept_graph,
            )
```

## Steps

### 1. Implement changes
### 2. Verify syntax: `python -c "import ast; ast.parse(open('services/reconciliation_queue.py').read()); print('Syntax OK')"`
### 3. Commit: `git add khawarizmi-backend/services/reconciliation_queue.py && git commit -m "feat(reconciliation): load concept graph from DB before FSRS update"`
