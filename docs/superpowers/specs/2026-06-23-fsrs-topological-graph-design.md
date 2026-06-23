# Graphe Topologique FSRS — Design Document

## Problème

Le graphe de dépendances entre micro-concepts est actuellement hardcodé dans `services/fsrs_graph.py` via le dict `CONCEPT_GRAPH` (6 entrées). La table `concept_prerequisites` existe déjà dans la DB (migration 001) mais n'est jamais utilisée par le code applicatif.

Par ailleurs, la sélection des concepts dus dans `fsrs_scheduler.py` trie uniquement par `due_date ASC, stability ASC` sans considérer l'ordre pédagogique (un concept dépendant ne devrait pas être révisé avant son prérequis).

## Solution

Approche A — Chirurgie minimale :
1. Remplacer `CONCEPT_GRAPH` hardcodé par un chargement depuis la DB avec cache TTL
2. Ajouter un tri topologique (Kahn) dans `get_due_concepts()` du scheduler
3. Passer le graphe aux fonctions de propagation

## Fichiers modifiés

### 1. `services/fsrs_graph.py`

**Nouvelle fonction asynchrone `load_concept_graph(db)`:**
- Requête `SELECT concept_id, prerequisite_id FROM concept_prerequisites`
- Construit un `Dict[str, List[str]]` (concept → [prérequis])
- Cache in-memory avec TTL de 300 secondes (5 min)
- Retourne le graphe

**Cache:**
```python
_graph_cache: Dict = {"data": {}, "timestamp": 0.0}
TTL = 300  # secondes
```

**Signature mise à jour de `update_concept_graph`:**
- Nouveau paramètre optionnel `graph: Optional[Dict[str, List[str]]] = None`
- Si `None`, lit depuis le cache (via `get_concept_graph()`)
- Le `graph` est passé aux deux fonctions de propagation

**Propagation mise à jour (`_propagate_prerequisite_penalties`, `_propagate_dependent_penalties`):**
- Nouveau paramètre `graph: Dict[str, List[str]]`
- Utilise `graph` au lieu du module-level `CONCEPT_GRAPH`

**Suppression:**
- La constante `CONCEPT_GRAPH` est supprimée

### 2. `services/fsrs_scheduler.py`

**Nouvelle fonction `_topological_sort(concept_ids, graph)` (Kahn):**
```python
def _topological_sort(concept_ids: List[str], graph: Dict[str, List[str]]) -> List[str]:
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
    return sorted_list + [c for c in concept_ids if c not in sorted_list]
```

**Modification de `get_due_concepts()`:**
- Paramètre optionnel supplémentaire `graph: Optional[Dict] = None`
- Si `graph` fourni, applique `_topological_sort()` sur les concept_ids avant le return
- Les prérequis passent avant les dépendants à stabilité égale

### 3. `routes/evaluate.py`

Avant l'appel à `update_concept_graph`:
```python
from services.fsrs_graph import load_concept_graph
graph = await load_concept_graph(db)
updates = update_concept_graph(..., graph=graph)
```

### 4. `services/reconciliation_queue.py`

Même pattern que `evaluate.py` : charger le graphe et le passer.

## Non modifié

Les 5+ autres points de requête qui lisent `mastery_micro_concepts` (flashcards.py, session.py, sessions.py, etc.) continuent de fonctionner sans changement. Ils lisent les mêmes données, juste sans tri topologique explicite — ce qui est acceptable car le graphe n'est critique que pour la sélection de la prochaine question.

## Tests

- Test unitaire : `_topological_sort()` avec graphe linéaire A→B→C, graphe en étoile, graphe vide
- Test intégration : `load_concept_graph()` retourne un dict correct depuis la DB
- Test propagation : vérifier que les pénalités prérequis/dépendant utilisent bien le graphe chargé
- Test régression : le scheduler existant retourne toujours des questions

## Ordre d'implémentation

1. `fsrs_graph.py` : remplacer CONCEPT_GRAPH, ajouter cache + load_concept_graph
2. `fsrs_scheduler.py` : ajouter _topological_sort, modifier get_due_concepts
3. `routes/evaluate.py` : charger le graphe avant update_concept_graph
4. `services/reconciliation_queue.py` : même pattern
5. Tests
