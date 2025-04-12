# Codex-Arch Testing Framework

This document outlines the comprehensive testing framework implemented for the Codex-Arch project, including test automation and CI/CD integration.

## Testing Approach

The Codex-Arch testing framework follows a multi-layered approach:

1. **Unit Tests** - Testing individual components in isolation
2. **Integration Tests** - Testing interactions between components
3. **End-to-End Tests** - Testing the complete system workflow

## Test Directory Structure

```
tests/
├── unit/            # Unit tests for individual modules
├── integration/     # Integration tests between components
├── e2e/             # End-to-end workflow tests
├── fixtures/        # Test fixtures and mock data
├── output/          # Test reports and coverage data
├── conftest.py      # Common pytest fixtures
└── run_e2e_tests.sh # Script for running E2E tests
```

## Running Tests

### Running All Tests

To run all tests with a single command, use the provided script:

```bash
./scripts/run_all_tests.sh
```

Options:
- `-v, --verbose` - Enable verbose output
- `--skip-e2e` - Skip end-to-end tests
- `--coverage-only` - Only generate coverage report
- `--ci` - Run in CI mode (includes JUnit reports)
- `--junit` - Generate JUnit reports
- `-h, --help` - Show help message

### Running E2E Tests Only

```bash
./tests/run_e2e_tests.sh
```

Options:
- `-v, --verbose` - Enable verbose output
- `-t, --test` - Run specific test(s)
- `--skip-slow` - Skip slow tests
- `--junit` - Generate JUnit XML report

### Using Tox

Run tests in multiple Python environments:

```bash
tox
```

Run specific test environments:

```bash
tox -e py39     # Run with Python 3.9
tox -e unit     # Run only unit tests
tox -e lint     # Run linting
tox -e coverage # Run coverage report
```

## CI/CD Integration

### GitHub Actions

The project includes GitHub Actions workflows for automated testing:

- `.github/workflows/run-tests.yml` - Runs tests on push/pull request

Key features:
- Matrix testing across Python versions
- Parallel execution of unit, integration, and E2E tests
- Combined test reports and coverage analysis
- Notifications on test failure

### CircleCI Configuration

Alternative CI/CD setup using CircleCI:

- `.circleci/config.yml` - CircleCI workflow configuration

Features:
- Sequential test execution (unit → integration → E2E)
- Artifact storage for test reports
- Coverage reporting to Codecov
- Slack notifications

## Test Coverage

We aim for a minimum of 80% code coverage. Coverage reports are generated in HTML and XML formats after test runs.

## Writing Tests

### Unit Tests

```python
def test_function_behavior():
    # Arrange
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

### Integration Tests

Integration tests should be marked with the `@pytest.mark.integration` decorator:

```python
@pytest.mark.integration
def test_component_interaction():
    # Test interaction between components
    pass
```

### End-to-End Tests

E2E tests should be marked with the `@pytest.mark.e2e` decorator:

```python
@pytest.mark.e2e
def test_complete_workflow():
    # Test a complete system workflow
    pass
```

## Test Data Management

- Use fixtures in `tests/fixtures/` for common test data
- Use `conftest.py` for shared pytest fixtures
- Mock external dependencies to ensure test isolation

## Best Practices

1. Keep tests independent and deterministic
2. Each test should focus on a single feature or behavior
3. Use descriptive test names that explain the expected behavior
4. Follow the Arrange-Act-Assert pattern
5. Avoid testing implementation details
6. Run tests regularly in the CI/CD pipeline
7. Aim for high code coverage but focus on meaningful tests

## Troubleshooting

### Common Issues

1. **Test dependency issues**: Ensure all test dependencies are installed with `pip install -e ".[test]"`
2. **Path issues**: Run tests from the project root directory
3. **Virtual environment**: Ensure the virtual environment is activated
4. **Test discovery**: Ensure test files follow the naming convention `test_*.py` 