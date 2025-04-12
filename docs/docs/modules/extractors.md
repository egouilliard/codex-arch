# Extractors Module

The Extractors module is responsible for parsing code files and extracting structural information from the codebase. It forms the foundation of the Codex-Arch analysis pipeline by providing the raw data needed for further processing.

## Overview

The Extractors module consists of several specialized extractors, each designed to extract specific types of information from the codebase:

- **File Tree Extractor**: Maps the directory and file structure
- **Python Dependency Extractor**: Identifies Python import statements and module dependencies
- **Code Structure Extractor**: Analyzes classes, functions, and other code elements

## Module Structure

```
extractors/
├── __init__.py         # Package exports
├── base.py             # Base extractor classes and interfaces
├── file_tree.py        # Directory and file extraction
├── python_imports.py   # Python import extraction
└── utils.py            # Utility functions for extraction
```

## Key Components

### FileTreeExtractor

The `FileTreeExtractor` traverses a directory structure and builds a hierarchical representation of the files and directories.

```python
from codex_arch.extractors import FileTreeExtractor

# Create an extractor instance
extractor = FileTreeExtractor(
    exclude_patterns=["node_modules", "*.pyc", "__pycache__"],
    max_depth=10
)

# Extract file tree from a directory
file_tree = extractor.extract("/path/to/project")

# Access the results
for file in file_tree.files:
    print(f"File: {file.path}, Size: {file.size} bytes")

for directory in file_tree.directories:
    print(f"Directory: {directory.path}, Files: {len(directory.files)}")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `exclude_patterns` | List of glob patterns to exclude | `[]` |
| `max_depth` | Maximum directory depth to traverse | `None` (unlimited) |
| `follow_symlinks` | Whether to follow symbolic links | `False` |
| `include_hidden` | Whether to include hidden files/dirs | `False` |

### PythonDependencyExtractor

The `PythonDependencyExtractor` analyzes Python files to identify import statements and extract dependency relationships between modules.

```python
from codex_arch.extractors import PythonDependencyExtractor

# Create an extractor instance
extractor = PythonDependencyExtractor(
    resolve_external=True,
    include_stdlib=False
)

# Extract dependencies from a Python file
dependencies = extractor.extract_file("/path/to/project/module.py")

# Or extract from an entire project
project_deps = extractor.extract_project("/path/to/project")

# Access the results
for dep in project_deps:
    print(f"Module {dep.source} imports {dep.target}")

# Get all modules that import a specific module
importers = project_deps.get_importers("package.module")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `resolve_external` | Try to resolve external dependencies | `True` |
| `include_stdlib` | Include standard library imports | `False` |
| `analyze_comments` | Check for imports in comments | `False` |
| `aliases` | Dict of import aliases to resolve | `{}` |

### CodeStructureExtractor

The `CodeStructureExtractor` analyzes code to identify classes, functions, and other structural elements.

```python
from codex_arch.extractors import CodeStructureExtractor

# Create an extractor instance
extractor = CodeStructureExtractor(
    include_docstrings=True,
    analyze_complexity=True
)

# Extract code structure from a file
structure = extractor.extract_file("/path/to/project/module.py")

# Access the results
for cls in structure.classes:
    print(f"Class: {cls.name}, Methods: {len(cls.methods)}")
    
    for method in cls.methods:
        print(f"  Method: {method.name}, Lines: {method.line_count}")

for func in structure.functions:
    print(f"Function: {func.name}, Complexity: {func.complexity}")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `include_docstrings` | Include docstrings in the analysis | `True` |
| `analyze_complexity` | Calculate complexity metrics | `True` |
| `include_private` | Include private members (prefixed with _) | `True` |
| `parse_type_hints` | Extract type hints from annotations | `True` |

## Usage in the Analysis Pipeline

The extractors are typically used as the first step in the analysis pipeline:

```python
from codex_arch.extractors import FileTreeExtractor, PythonDependencyExtractor
from codex_arch.analyzers import DependencyAnalyzer
from codex_arch.visualization import DependencyGraph

# Extract the file tree
file_tree = FileTreeExtractor().extract("/path/to/project")

# Extract dependencies
dependencies = PythonDependencyExtractor().extract_project("/path/to/project")

# Analyze dependencies
analyzer = DependencyAnalyzer()
dep_graph = analyzer.analyze(dependencies)

# Visualize the dependency graph
graph = DependencyGraph(dep_graph)
graph.render("dependencies.svg")
```

## Extension Points

The extractors module is designed to be extensible, allowing you to create custom extractors for specific needs:

```python
from codex_arch.extractors import BaseExtractor

class CustomExtractor(BaseExtractor):
    def __init__(self, custom_option=None):
        self.custom_option = custom_option
        
    def extract(self, path):
        # Implementation of custom extraction logic
        results = self._process_path(path)
        return results
    
    def _process_path(self, path):
        # Internal processing method
        pass
```

## API Reference

For a complete API reference, see the auto-generated [API documentation](../api/extractors.md).

## Relevant Files

The main implementation files for the extractors module:

- `codex_arch/extractors/__init__.py`: Package exports
- `codex_arch/extractors/file_tree.py`: File tree extraction
- `codex_arch/extractors/python_imports.py`: Python dependency extraction
- `codex_arch/extractors/base.py`: Base extractor classes

## Configuration Examples

### Example 1: Configuring Extractors in a Configuration File

```yaml
# codex-arch.yml
extractors:
  file_tree:
    exclude_patterns:
      - "node_modules"
      - "*.pyc"
      - "__pycache__"
      - ".git"
    max_depth: 10
    follow_symlinks: false
    include_hidden: false
    
  python_dependency:
    resolve_external: true
    include_stdlib: false
    analyze_comments: false
    aliases:
      np: numpy
      pd: pandas
      tf: tensorflow
```

### Example 2: Using Extractors from the Command Line

```bash
# Extract file tree
codex-arch extract file-tree --exclude="node_modules,*.pyc" /path/to/project

# Extract Python dependencies
codex-arch extract python-deps --resolve-external --no-stdlib /path/to/project

# Extract and analyze in one command
codex-arch analyze --extract-only --format=json /path/to/project > extracted_data.json
```

## Best Practices

- Configure appropriate exclusion patterns to avoid processing irrelevant files
- For large projects, use depth limits to focus on the most important parts
- Consider creating custom extractors for domain-specific needs
- Cache extraction results for performance in incremental analysis 