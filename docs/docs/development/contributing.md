# Contributing to Codex-Arch

Thank you for your interest in contributing to Codex-Arch! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct. Please report unacceptable behavior to [maintainers@codex-arch.com](mailto:maintainers@codex-arch.com).

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- GraphViz (for dependency visualization)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/codex-arch.git
   cd codex-arch
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/egouilliard/codex-arch.git
   ```

## Development Environment

### Setting Up

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev,test]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### IDE Configuration

If using VSCode, we recommend these settings:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

## Project Structure

```
codex-arch/
├── codex_arch/             # Main package
│   ├── extractors/         # File and dependency extraction modules
│   ├── metrics/            # Metrics collection
│   ├── visualization/      # Graph generation
│   ├── summary/            # Summary building
│   ├── bundler/            # Context bundle assembly
│   ├── cli/                # Command-line interface
│   ├── change_detection/   # Change detection
│   ├── api/                # REST API service
│   ├── hooks/              # Git hook integration
│   └── utils/              # Shared utilities
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example usages
├── scripts/                # Development scripts
└── .github/                # GitHub configuration
```

## Contribution Workflow

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**: Implement your feature or bug fix

3. **Add tests**: Write tests for your changes

4. **Run tests**: Ensure all tests pass
   ```bash
   pytest
   ```

5. **Run linting**: Ensure code quality
   ```bash
   flake8
   black .
   ```

6. **Commit your changes**: Use semantic commit messages
   ```bash
   git commit -m "feat: add new extraction method for JavaScript files"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a pull request**: Create a PR against the main repository

## Coding Standards

We follow these guidelines:

- **PEP 8**: Standard style guide for Python code
- **Black**: For code formatting
- **Type Hints**: Use type annotations for all functions and methods
- **Docstrings**: Document all public APIs using Google-style docstrings
- **Import Order**: Follow consistent import ordering (standard library → third-party → local)

Example:

```python
from typing import Dict, List, Optional
import os
import sys

import numpy as np
import pandas as pd

from codex_arch.utils import file_helper
from codex_arch.metrics import complexity


def calculate_metrics(
    file_path: str,
    include_complexity: bool = True
) -> Dict[str, any]:
    """Calculate metrics for a given file.

    Args:
        file_path: Path to the file to analyze
        include_complexity: Whether to include complexity metrics

    Returns:
        Dictionary containing the calculated metrics

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Implementation...
```

## Testing Guidelines

### Test Structure

- Place tests in the `tests/` directory mirroring the package structure
- Name test files with a `test_` prefix
- Name test functions/methods with a `test_` prefix
- Use pytest as the testing framework

### Testing Levels

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete workflows

### Test Coverage

We aim for minimum 80% code coverage. Run coverage with:

```bash
pytest --cov=codex_arch
```

### Mocking

Use `unittest.mock` or `pytest-mock` for mocking external dependencies:

```python
def test_file_analysis(mocker):
    # Arrange
    mock_file = mocker.patch("codex_arch.utils.file_helper.read_file")
    mock_file.return_value = "sample content"
    
    # Act
    result = analyze_file("dummy.py")
    
    # Assert
    assert result["lines"] == 1
    mock_file.assert_called_once_with("dummy.py")
```

## Documentation

### Code Documentation

- Add docstrings to all public modules, functions, classes, and methods
- Use Google-style docstrings
- Include examples where appropriate

### User Documentation

- Update relevant documentation in the `docs/` directory
- Add usage examples for new features
- For significant changes, update the corresponding guides

### Generate Documentation

To build the documentation locally:

```bash
cd docs
pip install -r requirements.txt
mkdocs serve
```

Then visit http://localhost:8000 to preview.

## Pull Request Process

1. **Create a descriptive PR**: Use our PR template and fill out all sections
2. **Link related issues**: Reference any related issues with "Fixes #123" or "Related to #123"
3. **CI checks**: Ensure all CI checks pass
4. **Code review**: Address feedback from code reviews
5. **Wait for approval**: At least one maintainer must approve before merging
6. **Merge**: A maintainer will merge your PR

### PR Template Sections

- **Description**: What does this PR do?
- **Related Issue**: Link to the issue this PR addresses
- **Motivation**: Why is this change needed?
- **Type of Change**: Bug fix, new feature, documentation, etc.
- **Testing**: How was it tested?
- **Checklist**: Tests added, docs updated, etc.

## Release Process

Our release process follows these steps:

1. **Prepare release**:
   - Update version in `setup.py` and `__init__.py`
   - Update CHANGELOG.md
   - Create a release PR

2. **Review and merge**:
   - Obtain approvals
   - Merge into main branch

3. **Tag and release**:
   - Tag the commit with version (e.g., `v1.2.0`)
   - Create a GitHub release
   - CI will publish to PyPI

4. **Announce**:
   - Announce the release in community channels

### Versioning

We follow Semantic Versioning (SemVer):

- **MAJOR**: Incompatible API changes
- **MINOR**: Add functionality in a backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

## Getting Help

If you need help:

- **Questions**: Ask in [GitHub Discussions](https://github.com/egouilliard/codex-arch/discussions)
- **Issues**: Report bugs in [GitHub Issues](https://github.com/egouilliard/codex-arch/issues)
- **Discord**: Join our [Discord community](https://discord.gg/codex-arch)

Thank you for contributing to Codex-Arch! 