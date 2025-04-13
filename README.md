# Task Master
### by [@eyaltoledano](https://x.com/eyaltoledano)

A task management system for AI-driven development with Claude, designed to work seamlessly with Cursor AI.

## Requirements

- Node.js 14.0.0 or higher
- Anthropic API key (Claude API)
- Anthropic SDK version 0.39.0 or higher

## Codex-Arch CLI Usage

Codex-Arch provides a command-line interface for analyzing code architecture. The CLI is built with Click and provides several commands for different types of analysis.

For detailed documentation, see [CLI Usage Guide](docs/cli_usage.md).

### Available Commands

- `analyze`: Analyze code structure and dependencies
- `index`: Index a code repository for faster searching and analysis
- `query`: Query code architecture data
- `report`: Generate a report about code architecture
- `changes`: Detect changes between Git commits
- `summarize`: Summarize changes between Git commits
- `dependencies`: Extract and analyze dependencies from Python code
- `filetree`: Extract and generate file trees from directories
- `hooks`: Manage Git hooks integration
- `run-all`: Run all analysis commands in sequence with visualization

### Basic Usage

```bash
# General format
python -m codex_arch.cli.cli [COMMAND] [OPTIONS]

# Examples
python -m codex_arch.cli.cli analyze path/to/repo --exclude-dirs=node_modules,dist
python -m codex_arch.cli.cli dependencies path/to/python/project
python -m codex_arch.cli.cli filetree path/to/directory -o tree.json
```

### Command-Specific Help

For detailed information about a specific command, use the `--help` option:

```bash
python -m codex_arch.cli.cli [COMMAND] --help

# Example
python -m codex_arch.cli.cli dependencies --help
```

### Note on CLI Implementation

Codex-Arch is transitioning from an argparse-based CLI to a click-based CLI. The old command style (`python -m codex_arch.cli.main [COMMAND]`) is still supported but deprecated. You will see deprecation warnings when using the old style. Please use the new click-based CLI as described above.

# Codex-Arch
### A tool for analyzing and visualizing code architecture

Codex-Arch is a comprehensive tool for analyzing code structure, dependencies, and metrics, then visualizing the results to provide insights into your codebase architecture.

## Requirements

- Python 3.7 or higher
- GraphViz (for visualization capabilities)
- Additional dependencies in requirements.txt

## Installation

```bash
# Clone the repository
git clone https://github.com/egouilliard/codex-arch.git
cd codex-arch

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start Guide

To quickly analyze a codebase:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run a full analysis with visualization
codex-arch run-all path/to/your/code --output output --convert-deps
```

## Command Reference

Codex-Arch provides a set of commands for different analysis tasks:

### 1. Extracting Dependencies

```bash
codex-arch dependencies <repo-path> [options]
```

**Example**:
```bash
codex-arch dependencies my_project --output output
```

### 2. Visualizing Dependencies

For effective visualization, use the included `generate_arch_graph.py` script:

```bash
python generate_arch_graph.py <dependency-json-file> <output-file-path>
```

**Example**:
```bash
python generate_arch_graph.py output/python_dependencies.json output/architecture_graph
```

This script generates detailed architecture visualizations in both SVG and PNG formats, highlighting:
- Module and submodule relationships
- Dependency counts between modules
- Core components of the application
- Visual grouping of related code

### 3. Converting Dependencies (Optional)

For more detailed visualization, you can convert the dependency format first:

```bash
python convert_deps.py <input-dependency-json> <output-converted-json>
python generate_arch_graph.py <output-converted-json> <output-file-path>
```

**Example**:
```bash
python convert_deps.py output/python_dependencies.json output/complete_dependencies.json
python generate_arch_graph.py output/complete_dependencies.json output/complete_arch_graph
```

### 4. Generating File Trees

```bash
codex-arch filetree <directory-path> [options]
```

**Example**:
```bash
codex-arch filetree my_project --output project_structure.json
```

### 5. Collecting Code Metrics

```bash
codex-arch metrics <directory-path> [options]
```

**Example**:
```bash
codex-arch metrics my_project --output project_metrics.json
```

### 6. Full Analysis Pipeline

```bash
codex-arch analyze <repo-path> [options]
```

**Example**:
```bash
codex-arch analyze my_project --output analysis_results --exclude-dirs venv .git node_modules
```

### 7. Complete End-to-End Analysis

The `run-all` command performs all analysis steps in sequence, including dependency extraction, metrics collection, file tree generation, and architecture visualization:

```bash
codex-arch run-all <repo-path> [options]
```

**Key Options**:
- `--output/-o <dir>`: Output directory for all results (default: './output')
- `--exclude-dirs/-d <dirs>`: Directories to exclude from all analyses
- `--convert-deps`: Convert dependency format for enhanced visualization
- `--no-visualization`: Skip architecture visualization
- `--no-metrics`: Skip metrics collection
- `--no-file-tree`: Skip file tree generation
- `--no-complexity`: Skip complexity analysis for faster processing

**Example**:
```bash
codex-arch run-all my_project --output analysis_results --exclude-dirs venv .git node_modules --convert-deps
```

This will run all analysis steps and generate both standard and enhanced architecture visualizations.

## Common Workflows

### Basic Code Analysis

```bash
# Activate virtual environment
source venv/bin/activate

# Generate dependency graph
codex-arch dependencies my_project --output output

# Generate architecture visualization
python generate_arch_graph.py output/python_dependencies.json output/architecture_graph

# Collect code metrics
codex-arch metrics my_project --output output/metrics.json
```

### Enhanced Visualization Workflow

```bash
# Generate dependency data
codex-arch dependencies my_project --output output

# Convert dependency format for better visualization
python convert_deps.py output/python_dependencies.json output/complete_dependencies.json

# Generate enhanced architecture graph
python generate_arch_graph.py output/complete_dependencies.json output/complete_arch_graph
```

### Complete Analysis with a Single Command

```bash
# Run all analysis steps with a single command
codex-arch run-all my_project --output analysis_results --exclude-dirs venv .git node_modules --convert-deps
```

This command performs:
1. Full code analysis (dependencies, metrics, file tree)
2. Dependency format conversion
3. Standard architecture graph generation
4. Enhanced architecture graph generation

The `run-all` command is ideal for getting a comprehensive analysis quickly without having to run multiple commands manually.

### Complete Analysis (Manual Steps)

```bash
# Activate virtual environment
source venv/bin/activate

# Run full analysis pipeline
codex-arch analyze my_project --output analysis_results --exclude-dirs venv .git node_modules

# Generate architecture visualization from the analysis
python generate_arch_graph.py analysis_results/python_dependencies.json analysis_results/architecture_graph
```

## Documentation

For detailed documentation on all commands and options, see [CLI Usage Guide](docs/cli_usage.md) or run:

```bash
codex-arch --help
codex-arch <command> --help
```