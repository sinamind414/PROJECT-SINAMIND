# Task 5: Write tests for topological sort + concept graph

**Goal:** Unit tests for `_topological_sort` function + integration test for `load_concept_graph`.

## Files
- Create: `khawarizmi-backend/tests/test_topological_sort.py`

## Test Cases

Write `khawarizmi-backend/tests/test_topological_sort.py` with:

```python
"""Tests for topological sort of concept dependencies."""

import pytest
from services.fsrs_scheduler import _topological_sort


class TestTopologicalSort:
    def test_linear_chain(self):
        """A -> B -> C: A before B before C."""
        concepts = ["C", "A", "B"]
        graph = {"A": ["B"], "B": ["C"]}
        result = _topological_sort(concepts, graph)
        assert result.index("A") < result.index("B")
        assert result.index("B") < result.index("C")

    def test_star_graph(self):
        """A -> B, A -> C, A -> D: A first."""
        concepts = ["B", "C", "A", "D"]
        graph = {"A": ["B", "C", "D"]}
        result = _topological_sort(concepts, graph)
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("A") < result.index("D")

    def test_empty_graph(self):
        """No dependencies: all returned unchanged."""
        concepts = ["X", "Y", "Z"]
        graph = {}
        result = _topological_sort(concepts, graph)
        assert len(result) == 3
        assert set(result) == {"X", "Y", "Z"}

    def test_single_concept(self):
        result = _topological_sort(["A"], {})
        assert result == ["A"]

    def test_diamond_graph(self):
        """A -> B, A -> C, B -> D, C -> D: A first, D last."""
        concepts = ["D", "B", "A", "C"]
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"]}
        result = _topological_sort(concepts, graph)
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")

    def test_cycle_in_graph(self):
        """A -> B -> A (cycle): no crash, all returned."""
        concepts = ["A", "B"]
        graph = {"A": ["B"], "B": ["A"]}
        result = _topological_sort(concepts, graph)
        assert len(result) == 2
        assert set(result) == {"A", "B"}

    def test_concepts_not_in_graph(self):
        """Graph has extra entries not in concept_ids — ignored."""
        concepts = ["B", "A"]
        graph = {"A": ["B"], "C": ["D"]}
        result = _topological_sort(concepts, graph)
        assert result.index("A") < result.index("B")

    def test_no_prerequisites_in_ids(self):
        """Concept has prerequisites not in the list — ignored."""
        concepts = ["A"]
        graph = {"A": ["B"]}  # B not in concept_ids
        result = _topological_sort(concepts, graph)
        assert result == ["A"]
```

## Steps

### 1. Write the test file
### 2. Run tests: `cd khawarizmi-backend && python -m pytest tests/test_topological_sort.py -v`
Expected: 8/8 passed
### 3. Commit:
```bash
git add khawarizmi-backend/tests/test_topological_sort.py
git commit -m "test(fsrs): add unit tests for topological sort"
```
