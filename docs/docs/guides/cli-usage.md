# Command Line Usage Guide

This guide provides detailed examples and best practices for using the Codex-Arch command-line interface (CLI) to analyze codebases and extract insights.

## Installation

Before using the Codex-Arch CLI, ensure you have installed the package as described in the [Installation Guide](../getting-started/installation.md).

## Basic Commands

### Analyzing a Project

The most common use case is analyzing a project directory:

```bash
codex-arch analyze /path/to/your/project
```

This command will:
1. Traverse the directory structure
2. Extract dependencies
3. Generate metrics
4. Produce a summary report

### Command Options

The `analyze` command supports various options to customize the analysis:

```bash
codex-arch analyze /path/to/project \
  --exclude "node_modules,dist,build" \
  --output-dir "./analysis-output" \
  --format json \
  --verbose
```

#### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--exclude`, `-e` | Comma-separated patterns to exclude | `node_modules,venv,__pycache__` |
| `--output-dir`, `-o` | Directory to store analysis results | `./output` |
| `--format`, `-f` | Output format (json, markdown, html) | `json` |
| `--verbose`, `-v` | Enable verbose output | `False` |
| `--config`, `-c` | Path to configuration file | `None` |

## Working with Analysis Results

### Generating Dependency Graphs

After analysis, you can generate visual dependency graphs:

```bash
codex-arch visualize ./output/dependencies.json \
  --output dependency-graph.svg \
  --layout hierarchical \
  --group-by module
```

#### Visualization Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output`, `-o` | Output file path | `dependency-graph.svg` |
| `--layout` | Graph layout (hierarchical, radial, force) | `hierarchical` |
| `--group-by` | Group nodes by (module, file, directory) | `None` |
| `--theme` | Visual theme (light, dark, colorful) | `light` |

### Generating Summary Reports

Create human-readable summaries from the analysis:

```bash
codex-arch summarize ./output/analysis-results.json \
  --template standard \
  --output project-summary.md
```

#### Summary Options

| Option | Description | Default |
|--------|-------------|---------|
| `--template` | Summary template (standard, detailed, minimal) | `standard` |
| `--output`, `-o` | Output file path | `summary.md` |
| `--include-metrics` | Include metrics in summary | `True` |

## Advanced Usage

### Using Configuration Files

Create a configuration file for reusable analysis settings:

```yaml
# codex-arch.yml
analyze:
  exclude:
    - "node_modules"
    - "dist"
    - "**/*.test.js"
  metrics:
    collect-complexity: true
    lines-of-code: true
  output-dir: "./analysis"
  format: "json"

visualize:
  layout: "hierarchical"
  theme: "colorful"
  group-by: "module"
```

Use the configuration file:

```bash
codex-arch analyze /path/to/project --config ./codex-arch.yml
```

### Change Detection

Analyze only changes between two Git commits:

```bash
codex-arch changes --base-commit HEAD~5 --target-commit HEAD
```

### Bundle Creation

Create a distributable bundle of architecture documentation:

```bash
codex-arch bundle \
  --input ./analysis-output \
  --output ./architecture-bundle.zip \
  --include-visualization \
  --include-summary
```

## Examples by Use Case

### Example 1: Quick Code Overview

For a quick overview of a new codebase:

```bash
codex-arch analyze /path/to/project \
  --format markdown \
  --template minimal \
  --metrics-level basic
```

### Example 2: Detailed Architecture Documentation

For comprehensive documentation:

```bash
codex-arch analyze /path/to/project \
  --format html \
  --template detailed \
  --metrics-level advanced \
  --include-visualization
```

### Example 3: Continuous Integration Usage

In a CI pipeline, use machine-readable output:

```bash
codex-arch analyze /path/to/project \
  --format json \
  --metrics-level comprehensive \
  --exit-on-complexity 15
```

## Troubleshooting

### Common Issues

1. **Analysis fails with memory error**
   
   For large codebases, increase available memory:
   ```bash
   CODEX_ARCH_MEMORY_LIMIT=4G codex-arch analyze /path/to/large/project
   ```

2. **Analysis is too slow**
   
   Exclude unnecessary directories:
   ```bash
   codex-arch analyze /path/to/project --exclude "node_modules,dist,test,examples"
   ```

3. **Cannot find Python dependencies**
   
   Ensure correct Python environment is active:
   ```bash
   codex-arch analyze /path/to/project --python-path /path/to/venv/bin/python
   ```

### Getting Help

Access the built-in help for any command:

```bash
codex-arch --help
codex-arch analyze --help
codex-arch visualize --help
```

## CLI Reference

For a complete reference of all available commands and options, see the [CLI Reference](../api/cli-reference.md). 