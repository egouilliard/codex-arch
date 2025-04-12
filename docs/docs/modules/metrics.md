# Metrics Module

The Metrics module collects and calculates various code metrics to provide insights into the size, complexity, and structure of the codebase. These metrics help in understanding the codebase characteristics and identifying potential issues.

## Overview

The Metrics module includes several specialized collectors for different types of metrics:

- **Size Metrics Collector**: Calculates code size metrics (lines of code, file counts, etc.)
- **Complexity Metrics Collector**: Calculates complexity metrics (cyclomatic complexity, cognitive complexity, etc.)
- **Dependency Metrics Collector**: Calculates dependency-related metrics (coupling, cohesion, etc.)

## Module Structure

```
metrics/
├── __init__.py         # Package exports
├── base.py             # Base metrics classes and interfaces
├── size.py             # Size metrics implementation
├── complexity.py       # Complexity metrics implementation
├── dependency.py       # Dependency metrics implementation
└── utils.py            # Utility functions for metrics calculation
```

## Key Components

### SizeMetricsCollector

The `SizeMetricsCollector` calculates size-related metrics for the codebase.

```python
from codex_arch.metrics import SizeMetricsCollector

# Create a collector instance
collector = SizeMetricsCollector(
    count_blank_lines=False,
    count_comments=False
)

# Calculate metrics for a file or directory
metrics = collector.collect("/path/to/project")

# Access the results
print(f"Total files: {metrics.total_files}")
print(f"Total lines of code: {metrics.total_loc}")
print(f"Average file size: {metrics.average_file_size} lines")

# Get per-language breakdown
for language, stats in metrics.by_language.items():
    print(f"{language}: {stats.loc} lines in {stats.files} files")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `count_blank_lines` | Whether to count blank lines in LOC | `False` |
| `count_comments` | Whether to count comment lines in LOC | `False` |
| `include_generated` | Whether to include generated files | `False` |
| `include_hidden` | Whether to include hidden files | `False` |

### ComplexityMetricsCollector

The `ComplexityMetricsCollector` calculates complexity metrics for functions and methods in the codebase.

```python
from codex_arch.metrics import ComplexityMetricsCollector

# Create a collector instance
collector = ComplexityMetricsCollector(
    metrics=["cyclomatic", "cognitive", "maintainability"],
    warning_threshold=10,
    error_threshold=20
)

# Calculate metrics for a file or directory
metrics = collector.collect("/path/to/project")

# Access the results
for file_path, file_complexity in metrics.by_file.items():
    print(f"File: {file_path}")
    print(f"  Average complexity: {file_complexity.average}")
    print(f"  Maximum complexity: {file_complexity.maximum}")
    
    # Get per-function complexity
    for func, func_complexity in file_complexity.functions.items():
        print(f"  Function: {func}")
        print(f"    Cyclomatic complexity: {func_complexity.cyclomatic}")
        print(f"    Cognitive complexity: {func_complexity.cognitive}")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `metrics` | List of complexity metrics to calculate | `["cyclomatic"]` |
| `warning_threshold` | Complexity value to trigger warning | `10` |
| `error_threshold` | Complexity value to trigger error | `20` |
| `per_function` | Whether to calculate metrics per function | `True` |
| `include_nested` | Whether to include nested functions | `True` |

### DependencyMetricsCollector

The `DependencyMetricsCollector` calculates dependency-related metrics like coupling and cohesion.

```python
from codex_arch.metrics import DependencyMetricsCollector

# Create a collector instance
collector = DependencyMetricsCollector(
    metrics=["afferent_coupling", "efferent_coupling", "instability"],
    granularity="module"
)

# Calculate metrics based on a dependency graph
dep_graph = dependency_analyzer.analyze_project("/path/to/project")
metrics = collector.collect(dep_graph)

# Access the results
for module, module_metrics in metrics.by_module.items():
    print(f"Module: {module}")
    print(f"  Afferent coupling (Ca): {module_metrics.afferent_coupling}")
    print(f"  Efferent coupling (Ce): {module_metrics.efferent_coupling}")
    print(f"  Instability (I): {module_metrics.instability}")
    print(f"  Abstractness (A): {module_metrics.abstractness}")
    
# Find modules with high coupling
high_coupling = metrics.find_modules(
    lambda m: m.afferent_coupling + m.efferent_coupling > 10
)
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `metrics` | List of dependency metrics to calculate | `["afferent_coupling", "efferent_coupling"]` |
| `granularity` | Level of granularity for metrics (file, module, package) | `"module"` |
| `normalize` | Whether to normalize metric values | `True` |
| `include_external` | Whether to include external dependencies | `False` |

## Usage in the Analysis Pipeline

The metrics module is typically used after the extraction and analysis phases:

```python
from codex_arch.extractors import FileTreeExtractor, PythonDependencyExtractor
from codex_arch.analyzers import DependencyAnalyzer
from codex_arch.metrics import SizeMetricsCollector, ComplexityMetricsCollector, DependencyMetricsCollector

# Extract the file tree
file_tree = FileTreeExtractor().extract("/path/to/project")

# Extract and analyze dependencies
dependencies = PythonDependencyExtractor().extract_project("/path/to/project")
dep_graph = DependencyAnalyzer().analyze(dependencies)

# Calculate metrics
size_metrics = SizeMetricsCollector().collect(file_tree)
complexity_metrics = ComplexityMetricsCollector().collect("/path/to/project")
dependency_metrics = DependencyMetricsCollector().collect(dep_graph)

# Combine metrics into a report
metrics_report = {
    "size": size_metrics.to_dict(),
    "complexity": complexity_metrics.to_dict(),
    "dependency": dependency_metrics.to_dict()
}

# Export metrics to JSON
import json
with open("metrics_report.json", "w") as f:
    json.dump(metrics_report, f, indent=2)
```

## Extension Points

The metrics module provides a flexible extension mechanism for custom metrics:

```python
from codex_arch.metrics import BaseMetricsCollector

class CustomMetricsCollector(BaseMetricsCollector):
    """Custom metrics collector for specific project needs."""
    
    def __init__(self, custom_option=None):
        self.custom_option = custom_option
        
    def collect(self, target):
        """Collect custom metrics from the target."""
        # Implementation of custom metrics collection
        results = self._process_target(target)
        return results
    
    def _process_target(self, target):
        # Internal processing method
        pass
```

## API Reference

For a complete API reference, see the auto-generated [API documentation](../api/metrics.md).

## Relevant Files

The main implementation files for the metrics module:

- `codex_arch/metrics/__init__.py`: Package exports
- `codex_arch/metrics/size.py`: Size metrics implementation
- `codex_arch/metrics/complexity.py`: Complexity metrics implementation
- `codex_arch/metrics/dependency.py`: Dependency metrics implementation
- `codex_arch/metrics/base.py`: Base metrics classes

## Configuration Examples

### Example 1: Configuring Metrics in a Configuration File

```yaml
# codex-arch.yml
metrics:
  size:
    count_blank_lines: false
    count_comments: true
    include_generated: false
    include_hidden: false
    
  complexity:
    metrics:
      - cyclomatic
      - cognitive
      - maintainability
    warning_threshold: 15
    error_threshold: 25
    per_function: true
    include_nested: true
    
  dependency:
    metrics:
      - afferent_coupling
      - efferent_coupling
      - instability
      - abstractness
    granularity: module
    normalize: true
    include_external: false
    
  custom:
    - name: test_coverage
      path: "./metrics/coverage.py"
      class: "CoverageMetricsCollector"
      enabled: true
```

### Example 2: Using Metrics from the Command Line

```bash
# Calculate all metrics
codex-arch metrics --all /path/to/project

# Calculate specific metrics
codex-arch metrics --types=size,complexity /path/to/project

# Calculate metrics with custom thresholds
codex-arch metrics --complexity.warning=12 --complexity.error=20 /path/to/project

# Export metrics to JSON
codex-arch metrics --all --format=json --output=metrics.json /path/to/project
```

## Best Practices

- Configure appropriate thresholds for your project's specific needs
- Use metrics as indicators, not absolute measures of code quality
- Track metrics over time to identify trends and improvements
- Focus on improving the most critical metrics first
- Combine multiple metrics for a comprehensive view of the codebase
- Create custom metrics for domain-specific needs 