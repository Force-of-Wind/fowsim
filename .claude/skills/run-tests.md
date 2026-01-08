---
description: Run the test suite with pytest
---

# Run Tests

Execute the project test suite using pytest.

## Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=cardDatabase --cov-report=term-missing

# Run specific test file
pytest cardDatabase/tests/test_models.py

# Run tests matching a pattern
pytest -k "test_deck"

# Run and stop on first failure
pytest -x

# Run failed tests from last run
pytest --lf
```

## Writing Tests

Place test files in `cardDatabase/tests/` with names like `test_*.py`.

Example test structure:

```python
import pytest
from django.test import Client
from cardDatabase.models import Card, DeckList

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def sample_card(db):
    return Card.objects.create(name="Test Card", ...)

def test_card_str(sample_card):
    assert str(sample_card) == "Test Card"

@pytest.mark.django_db
def test_deck_creation(client):
    # Test deck creation flow
    pass
```

## Notes

- Use `@pytest.mark.django_db` for tests that need database access
- Use fixtures for common test setup
- Test both success and error cases
