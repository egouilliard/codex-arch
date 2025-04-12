# Quick Start Guide

This guide will help you get started with Codex-Arch quickly by walking through basic operations and common use cases.

## Basic Usage

After [installing Codex-Arch](installation.md), you can start analyzing your codebase with a simple command:

```bash
codex-arch analyze /path/to/your/project
```

This will:
1. Scan your project directory
2. Extract the file tree structure
3. Analyze dependencies and imports
4. Generate basic metrics
5. Create a summary report in the `output` directory

## Command Line Interface

Codex-Arch provides a comprehensive CLI with various commands and options:

### Analyze Command

The main command for code analysis:

```bash
codex-arch analyze [OPTIONS] PROJECT_PATH
```

**Common Options:**

- `--output-dir, -o`: Specify output directory (default: `./output`)
- `--format, -f`: Output format (`json`, `markdown`, `html`, default: `json`)
- `--exclude, -e`: Patterns to exclude (e.g., `--exclude="node_modules,*.pyc"`)
- `--verbose, -v`: Show detailed progress
- `--config, -c`: Path to config file

### Visualize Command

Generate dependency graphs:

```bash
codex-arch visualize [OPTIONS] PROJECT_PATH
```

**Common Options:**

- `--output-file, -o`: Output file name (default: `dependency_graph.svg`)
- `--format, -f`: Output format (`svg`, `png`, `dot`, default: `svg`)
- `--include-external`: Include external dependencies
- `--group-by`: Group nodes by (`module`, `package`, `directory`, default: `module`)

### Summary Command

Generate project summary:

```bash
codex-arch summary [OPTIONS] PROJECT_PATH
```

**Common Options:**

- `--format, -f`: Output format (`markdown`, `html`, `json`, default: `markdown`)
- `--include-metrics`: Include code metrics
- `--include-dependencies`: Include dependency information

## Examples

### Example 1: Basic Analysis

```bash
# Generate a basic analysis with default settings
codex-arch analyze ~/projects/my-python-app

# Review the output
ls -la output/
```

### Example 2: Custom Analysis with Exclusions

```bash
# Analyze excluding tests and documentation
codex-arch analyze --exclude="tests,docs,*.md" --output-dir="my-analysis" ~/projects/my-app
```

### Example 3: Generate Dependency Graph

```bash
# Create an SVG visualization of the project dependencies
codex-arch visualize --output-file="dependencies.svg" ~/projects/my-app

# Group by package
codex-arch visualize --group-by="package" ~/projects/my-app
```

### Example 4: Create a Markdown Summary

```bash
# Generate a comprehensive markdown summary
codex-arch summary --format="markdown" --include-metrics --include-dependencies ~/projects/my-app
```

## Using Configuration Files

For complex setups, you can create a configuration file:

```yaml
# codex-arch.yml
project:
  path: "./src"
  exclude: 
    - "node_modules"
    - "dist"
    - "*.test.js"

output:
  directory: "./analysis-output"
  format: "html"

visualization:
  format: "svg"
  group_by: "package"
  include_external: false
```

Then run:

```bash
codex-arch analyze --config="codex-arch.yml"
```

## Working with the REST API

If you've set up the REST API service, you can use it to analyze projects:

```bash
# Start the API server
codex-arch api serve --port=5000

# Use the API
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/project", "exclude": ["node_modules"]}'
```

## Next Steps

Now that you've learned the basics, you might want to explore:

- [Configuration options](configuration.md) for customizing Codex-Arch
- [CLI usage guide](../guides/cli-usage.md) for more advanced command options
- [API integration](../guides/api-integration.md) for using Codex-Arch programmatically
- [Git hook setup](../guides/git-hook-setup.md) for automating analysis on code changes 