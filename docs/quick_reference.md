# Codex-Arch Quick Reference Guide

This quick reference provides the most common commands and examples for using Codex-Arch to analyze code architecture.

## Setup

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Core Commands

### Extract Dependencies

```bash
# Basic dependency extraction
codex-arch dependencies my_project --output analysis_results

# Exclude specific directories
codex-arch dependencies my_project --exclude-patterns "**/tests/**" "**/docs/**"
```

### Visualize Dependencies

```bash
# Generate a dependency graph
codex-arch visualize analysis_results/python_dependencies.json --output dependency_graph.svg

# Change visualization theme
codex-arch visualize analysis_results/python_dependencies.json --output dependency_graph.svg --theme dark

# Limit to most important nodes
codex-arch visualize analysis_results/python_dependencies.json --max-nodes 50
```

### Generate Architecture Diagrams

```bash
# Generate dependency information
codex-arch dependencies my_project --output architecture_analysis

# Create visualization in SVG format
codex-arch visualize architecture_analysis/python_dependencies.json --output architecture_analysis/dependency_graph.svg --group-modules

# Create visualization in DOT format (for further customization)
codex-arch visualize architecture_analysis/python_dependencies.json --output architecture_analysis/dependency_graph.dot --format dot

# Generate enhanced architecture diagram using the custom script
python generate_arch_graph.py architecture_analysis/python_dependencies.json architecture_analysis/architecture_graph
```

### Generate File Trees

```bash
# Create a JSON file tree
codex-arch filetree my_project --output project_structure.json

# Create a markdown file tree
codex-arch filetree my_project --format markdown --output project_structure.md
```

### Collect Code Metrics

```bash
# Basic metrics collection
codex-arch metrics my_project --output project_metrics.json

# Skip complexity analysis for faster processing
codex-arch metrics my_project --output project_metrics.json --no-complexity
```

### Run Full Analysis

```bash
# Complete analysis pipeline 
codex-arch analyze my_project --output full_analysis

# Exclude common directories
codex-arch analyze my_project --output full_analysis --exclude-dirs venv .git node_modules
```

## Common Workflows

### Basic Dependency Analysis

```bash
# 1. Generate dependency graph
codex-arch dependencies my_project --output analysis

# 2. Visualize dependencies
codex-arch visualize analysis/python_dependencies.json --output analysis/dependency_graph.svg
```

### Comprehensive Project Analysis

```bash
# 1. Create file tree
codex-arch filetree my_project --output analysis/file_tree.json

# 2. Generate dependency graph
codex-arch dependencies my_project --output analysis

# 3. Collect code metrics
codex-arch metrics my_project --output analysis/metrics.json

# 4. Visualize dependencies
codex-arch visualize analysis/python_dependencies.json --output analysis/dependency_graph.svg
```

### Focused Analysis (Specific Directory)

```bash
# Analyze only the src directory
codex-arch dependencies my_project/src --output src_analysis
codex-arch visualize src_analysis/python_dependencies.json --output src_analysis/dependency_graph.svg
```

### Generate Comprehensive Architecture Diagram

```bash
# 1. Generate dependency data
codex-arch dependencies my_project --output architecture_analysis

# 2. Generate the architecture diagram using the custom script
python generate_arch_graph.py architecture_analysis/python_dependencies.json architecture_analysis/architecture_graph

# 3. The diagram will be available in both SVG and PNG formats
# - architecture_analysis/architecture_graph.svg
# - architecture_analysis/architecture_graph.png
```

## Tips

- Use `--help` to see all options for any command: `codex-arch dependencies --help`
- For large projects, analyze specific directories separately
- Use `--exclude-dirs` to skip non-code directories
- SVG visualizations offer better interactivity than PNG
- Use `--group-modules` for more readable dependency graphs

## Known Issues

- If summary generation fails, use individual commands instead
- If visualization reports 0 nodes/edges but generates a file, the file is likely correct
- For very large codebases, use file pattern filtering to focus analysis

For more detailed usage information, see [CLI Usage Guide](cli_usage.md) 