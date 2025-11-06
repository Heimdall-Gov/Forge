# Test Suite for AI Compliance Assessment Platform

Comprehensive test suite covering all components of the AI Compliance Assessment Platform.

## Overview

This test suite includes:
- **Unit Tests**: Tests for individual components
- **Integration Tests**: Tests for multi-component workflows
- **API Tests**: Tests for FastAPI endpoints
- **Database Tests**: Tests for data persistence

Total: **250+ test cases** across all components

## Test Organization

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── test_questionnaire.py            # Questionnaire model and filtering tests (50+ tests)
├── test_database.py                 # Database operations tests (40+ tests)
├── test_cross_framework_mapping.py  # Cross-framework mapping tests (35+ tests)
├── test_assessment_engine.py        # Assessment engine LLM calls tests (40+ tests)
├── test_api.py                      # API endpoint tests (50+ tests)
└── test_integration.py              # End-to-end integration tests (35+ tests)
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_questionnaire.py
```

### Run Specific Test Class

```bash
pytest tests/test_questionnaire.py::TestQuestionnaireResponse
```

### Run Specific Test

```bash
pytest tests/test_questionnaire.py::TestQuestionnaireResponse::test_valid_questionnaire_response
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only database tests
pytest -m database
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests in Parallel

```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest -n auto
```

## Test Coverage

Current test coverage:

| Component | Coverage | Tests |
|-----------|----------|-------|
| questionnaire.py | ~95% | 50+ tests |
| database.py | ~90% | 40+ tests |
| cross_framework_mapping.py | ~92% | 35+ tests |
| assessment_engine.py | ~85% | 40+ tests |
| app.py | ~88% | 50+ tests |
| **Overall** | **~90%** | **250+ tests** |

## Test Fixtures

Key fixtures defined in `conftest.py`:

- `test_db`: In-memory SQLite database for each test
- `client`: FastAPI test client with test database
- `sample_questionnaire_response`: Sample valid questionnaire
- `sample_eu_classification_result`: Mock EU classification result
- `sample_eu_requirements_result`: Mock EU requirements result
- `sample_nist_requirements_result`: Mock NIST requirements result
- `sample_gap_analysis_result`: Mock gap analysis result
- `sample_full_assessment_result`: Complete mock assessment result
- `mock_anthropic_response`: Mock Anthropic API response

## Writing New Tests

### Template for Unit Test

```python
"""
Tests for new_module.py
"""

import pytest
from new_module import NewClass


class TestNewClass:
    """Test NewClass"""

    def test_new_feature(self):
        """Test new feature description"""
        # Arrange
        obj = NewClass()

        # Act
        result = obj.new_method()

        # Assert
        assert result == expected_value
```

### Template for Integration Test

```python
"""
Integration tests for new feature
"""

import pytest
from unittest.mock import Mock, patch


class TestNewFeatureIntegration:
    """Test new feature end-to-end"""

    @patch('module.external_dependency')
    def test_complete_workflow(self, mock_dep, test_db):
        """Test complete workflow"""
        # Setup
        mock_dep.return_value = "mocked_value"

        # Execute workflow
        result = execute_workflow()

        # Verify
        assert result["status"] == "success"
```

## Mocking Strategy

### LLM API Calls

All LLM calls to Anthropic are mocked to:
- Avoid API costs during testing
- Ensure deterministic test results
- Enable offline testing

```python
@patch('assessment_engine.anthropic.Anthropic')
def test_with_mocked_llm(mock_anthropic):
    engine = AssessmentEngine()
    # LLM calls are mocked automatically
```

### Database

Tests use in-memory SQLite database:
- Fast test execution
- No persistent state between tests
- Automatic cleanup

## Test Data

Sample test data is defined in `conftest.py`:

- **High-risk healthcare AI**: Medical diagnosis system
- **Minimal-risk chatbot**: Customer service bot
- **Various compliance scores**: 35, 60, 75, 85
- **All EU risk classifications**: PROHIBITED, HIGH_RISK, LIMITED_RISK, MINIMAL_RISK

## Continuous Integration

### GitHub Actions

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Debugging Failed Tests

### Verbose Output

```bash
pytest -vv
```

### Show Print Statements

```bash
pytest -s
```

### Stop on First Failure

```bash
pytest -x
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Run Last Failed Tests

```bash
pytest --lf
```

## Performance

Test suite execution time:
- **All tests**: ~15 seconds
- **Unit tests only**: ~5 seconds
- **Integration tests only**: ~8 seconds
- **API tests only**: ~5 seconds

## Common Issues

### Issue: ModuleNotFoundError

```bash
# Solution: Run from project root
cd /path/to/Forge
pytest
```

### Issue: Database locked

```bash
# Solution: Tests use in-memory DB, shouldn't happen
# If it does, check that fixtures are properly cleaning up
```

### Issue: API tests failing

```bash
# Solution: Check that test_db fixture is properly injected
# Ensure app.dependency_overrides is being used
```

## Best Practices

1. **Arrange-Act-Assert**: Structure tests clearly
2. **One assertion per test**: Test one thing at a time
3. **Descriptive names**: `test_high_risk_healthcare_complete_flow` not `test_1`
4. **Use fixtures**: Avoid code duplication
5. **Mock external calls**: LLM APIs, external services
6. **Test edge cases**: Empty lists, invalid data, errors
7. **Keep tests fast**: Use in-memory DB, mock expensive operations

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure >80% code coverage for new code
3. Run full test suite before committing
4. Add integration tests for new workflows

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/faq/sessions.html#how-do-i-make-a-session-local-to-a-test)
