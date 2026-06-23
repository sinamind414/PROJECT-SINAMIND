# Task 2 Report — Topological sort in fsrs_scheduler.py

**Status:** DONE

**Commit:** `3ce8848` (`feat(fsrs): add topological sort to get_due_concepts`)

**Changes made:**
1. Added `from collections import deque` import (line 8)
2. Added `_topological_sort()` function implementing Kahn algorithm (lines 16–40)
3. Added topological sort integration in `get_due_concepts()` — after building the due_concepts list, calls `load_concept_graph(db)` to get the prerequisite graph, then sorts due concepts so prerequisites appear before dependents, with stability as secondary sort key. Falls back gracefully on any error.

**Verification:** `python -c "import ast; ast.parse(...)"` — Syntax OK

**Concerns:** None
