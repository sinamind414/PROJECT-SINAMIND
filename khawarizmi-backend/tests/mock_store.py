"""Shared in-memory mock store for test fixtures.

Conftest and test files import from here to avoid circular
import issues with pytest's special conftest.py handling.
"""

mock_store: dict = {}
inserted_emails: set[str] = set()
