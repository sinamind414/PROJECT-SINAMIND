# Task 3: Update `routes/evaluate.py` — load graph before FSRS update

**Goal:** Load concept dependency graph from DB before calling `update_concept_graph`, passing it as the `graph=` parameter.

## Consumes (from Task 1)
- `load_concept_graph(db)` — async, returns `Dict[str, List[str]]`
- `update_concept_graph(..., graph=graph)` — accepts optional graph

## Files
- Modify: `khawarizmi-backend/routes/evaluate.py` (around line 174)

## Change

Before the `updates = update_concept_graph(` call (currently around line 174-182), insert:

```python
        # Charger le graphe de dépendances depuis la DB
        from services.fsrs_graph import load_concept_graph
        concept_graph = await load_concept_graph(db)
```

And in the `update_concept_graph(` call, add `graph=concept_graph` to the keyword arguments (before the closing `)`).

So the existing:
```python
        updates = update_concept_graph(
            user_id=user_id,
            ...
            user_fsrs_config=user_fsrs_config
        )
```

Becomes:
```python
        # Charger le graphe de dépendances depuis la DB
        from services.fsrs_graph import load_concept_graph
        concept_graph = await load_concept_graph(db)

        updates = update_concept_graph(
            user_id=user_id,
            ...
            user_fsrs_config=user_fsrs_config,
            graph=concept_graph,
        )
```

## Steps

### 1. Implement changes
### 2. Verify syntax: `python -c "import ast; ast.parse(open('routes/evaluate.py').read()); print('Syntax OK')"`
### 3. Commit: `git add khawarizmi-backend/routes/evaluate.py && git commit -m "feat(evaluate): load concept graph from DB before FSRS update"`
