# Codex-Arch CLI Implementation Checklist

## Project Structure Setup

- [ ] Update project dependencies in `packages/cli/package.json`:
  - [ ] Add/update `commander` for CLI command support
  - [ ] Add `chalk` for colored terminal output
  - [ ] Add `table` for formatted table output
  - [ ] Add `ora` for spinners and progress indicators
  - [ ] Add `figlet` for CLI banner display
  - [ ] Add `inquirer` for interactive prompts
  - [ ] Add `boxen` for terminal boxes
  - [ ] Add `conf` for configuration management
  - [ ] Add `open` for opening browser windows

- [ ] Create directory structure for CLI commands:
  ```
  packages/cli/
  ├── src/
  │   ├── index.ts                      # Main CLI entry point
  │   ├── commands/                     # Commands directory
  │   │   ├── analyze.ts                # Analyze command
  │   │   ├── query/                    # Query commands directory
  │   │   │   ├── index.ts              # Query command entry point
  │   │   │   ├── dependencies.ts       # Dependencies command
  │   │   │   ├── imports.ts            # Imports command
  │   │   │   ├── importers.ts          # Importers command
  │   │   │   ├── most-imported.ts      # Most-imported command
  │   │   │   ├── isolated.ts           # Isolated files command
  │   │   │   ├── connection.ts         # Connection path command
  │   │   │   ├── clusters.ts           # Clusters command
  │   │   │   └── custom.ts             # Custom query command
  │   │   ├── visualize.ts              # Visualize command
  │   │   └── run.ts                    # Run command
  │   ├── utils/                        # Utilities directory
  │   │   ├── config.ts                 # Configuration utilities
  │   │   ├── database.ts               # Database connection utilities
  │   │   ├── formatters.ts             # Output formatting utilities
  │   │   └── visualization.ts          # Visualization utilities
  │   └── types/                        # Types directory
  │       └── index.ts                  # Type definitions
  ```

## Step 1: Create Core Utilities

- [ ] Create `packages/cli/src/types/index.ts` to define common types:
  - [ ] Define `CodexConfig` interface
  - [ ] Define `QueryResult` interfaces
  - [ ] Define `VisualizationOptions` interface

- [ ] Create `packages/cli/src/utils/config.ts` for configuration management:
  - [ ] Implement `loadConfig()` function to load from file/CLI options
  - [ ] Implement config file creation/saving
  - [ ] Implement output directory management

- [ ] Create `packages/cli/src/utils/database.ts` for Neo4j connection:
  - [ ] Implement `connectToNeo4j()` function
  - [ ] Implement Docker Neo4j container management
  - [ ] Add connection validation functionality

- [ ] Create `packages/cli/src/utils/formatters.ts` for output formatting:
  - [ ] Implement `formatAsTable()` function
  - [ ] Implement `formatAsJSON()` function
  - [ ] Implement `formatAsTree()` function
  - [ ] Create a main `formatOutput()` function

- [ ] Create `packages/cli/src/utils/visualization.ts` for visualization helpers:
  - [ ] Implement HTML template generation
  - [ ] Implement `generateVisualization()` function
  - [ ] Implement `openVisualization()` function

## Step 2: Core CLI Structure Implementation

- [ ] Modify `packages/cli/src/index.ts`:
  - [ ] Setup Commander program with global options
  - [ ] Add banner with figlet
  - [ ] Register all command modules
  - [ ] Add error handling for unexpected errors

## Step 3: Implement Analyze Command

- [ ] Create `packages/cli/src/commands/analyze.ts`:
  - [ ] Define analyze command structure
  - [ ] Add directory argument with default to current directory
  - [ ] Add options for exclude/include patterns
  - [ ] Add output file option
  - [ ] Implement directory validation
  - [ ] Connect to TypeScript parser from @codex-arch/parsers-typescript
  - [ ] Add progress reporting

## Step 4: Implement Query Commands

- [ ] Create `packages/cli/src/commands/query/index.ts`:
  - [ ] Create query command base
  - [ ] Register all subcommands
  - [ ] Add shared query options

- [ ] Create `packages/cli/src/commands/query/dependencies.ts`:
  - [ ] Add file-path argument
  - [ ] Add depth option (default: 1)
  - [ ] Add reverse flag for reverse dependencies
  - [ ] Add format option
  - [ ] Implement direct dependency querying logic
  - [ ] Implement dependency chain querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/imports.ts`:
  - [ ] Add file-path argument
  - [ ] Add depth option (default: 1)
  - [ ] Add format option
  - [ ] Implement import querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/importers.ts`:
  - [ ] Add file-path argument
  - [ ] Add depth option (default: 1)
  - [ ] Add format option
  - [ ] Implement importer querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/most-imported.ts`:
  - [ ] Add limit option (default: 10)
  - [ ] Add format option
  - [ ] Implement most-imported files querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/isolated.ts`:
  - [ ] Add format option
  - [ ] Implement isolated files querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/connection.ts`:
  - [ ] Add two file-path arguments
  - [ ] Add max-depth option (default: 4)
  - [ ] Add format option
  - [ ] Implement connection path querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/clusters.ts`:
  - [ ] Add min-size option (default: 3)
  - [ ] Add format option
  - [ ] Implement file clustering querying logic
  - [ ] Format and display results

- [ ] Create `packages/cli/src/commands/query/custom.ts`:
  - [ ] Add cypher-query argument
  - [ ] Add param option for query parameters
  - [ ] Add format option
  - [ ] Implement custom query execution
  - [ ] Format and display results

## Step 5: Implement Visualize Command

- [ ] Create `packages/cli/src/commands/visualize.ts`:
  - [ ] Add directory argument with default to current directory
  - [ ] Add type option (dependency-graph, cluster-graph)
  - [ ] Add output option for output file path
  - [ ] Add format option (html, json, d3)
  - [ ] Add open flag to open in browser
  - [ ] Implement visualization data generation
  - [ ] Implement HTML template generation
  - [ ] Implement browser opening logic

## Step 6: Implement Run Command

- [ ] Create `packages/cli/src/commands/run.ts`:
  - [ ] Add directory argument with default to current directory
  - [ ] Add exclude/include options for patterns
  - [ ] Add skip-analysis flag
  - [ ] Add skip-visualization flag
  - [ ] Add skip-browser flag
  - [ ] Implement directory validation
  - [ ] Implement Neo4j Docker container management
  - [ ] Implement full workflow:
    - [ ] Run TypeScript analysis
    - [ ] Check/start Neo4j
    - [ ] Import analysis data into Neo4j
    - [ ] Generate visualization
    - [ ] Open browser (if not skipped)
  - [ ] Add progress reporting with ora
  - [ ] Handle errors gracefully

## Step 7: Refactoring Existing Scripts

- [ ] Extract query functionality from `scripts/test-graphiti-queries.ts`:
  - [ ] Move query methods to reusable modules
  - [ ] Standardize parameter handling

- [ ] Extract visualization code from visualization scripts:
  - [ ] Create reusable visualization modules
  - [ ] Standardize output file handling

- [ ] Update any dependent scripts to use new CLI commands

## Step 8: Implement Core Query Library

- [ ] Create query library in `packages/core/src/queries/`:
  - [ ] Move all query logic from test scripts to this library
  - [ ] Create `directDependencies.ts`
  - [ ] Create `reverseDependencies.ts`
  - [ ] Create `dependencyChains.ts`
  - [ ] Create `mostImported.ts`
  - [ ] Create `isolatedFiles.ts`
  - [ ] Create `fileClustering.ts`
  - [ ] Create `connectionPath.ts`
  - [ ] Export all query functions from an index file

## Step 9: Testing and Documentation

- [ ] Write tests for each CLI command:
  - [ ] Unit tests for utility functions
  - [ ] Integration tests for commands

- [ ] Update documentation:
  - [ ] Create README with examples for each command
  - [ ] Update project documentation with CLI usage
  - [ ] Add help text for each command

## Step 10: Detailed Implementation Task List for Each Command

### Analyze Command
- [ ] Implement directory argument handling
- [ ] Implement exclude/include pattern parsing
- [ ] Implement TypeScript analysis logic
- [ ] Implement output file handling
- [ ] Add progress reporting
- [ ] Handle errors gracefully

### Dependencies Command
- [ ] Implement file-path argument validation
- [ ] Implement depth option parsing
- [ ] Implement reverse flag handling
- [ ] Implement direct dependency query
- [ ] Implement dependency chain query
- [ ] Add output formatting based on format option

### Imports Command
- [ ] Implement file-path argument validation
- [ ] Implement depth option parsing
- [ ] Implement import relationship query
- [ ] Add output formatting

### Importers Command
- [ ] Implement file-path argument validation
- [ ] Implement depth option parsing
- [ ] Implement reverse import relationship query
- [ ] Add output formatting

### Most-Imported Command
- [ ] Implement limit option parsing
- [ ] Implement most-imported files query
- [ ] Add sorting by import count
- [ ] Add output formatting

### Isolated Command
- [ ] Implement isolated files query
- [ ] Add output formatting

### Connection Command
- [ ] Implement two file-path arguments validation
- [ ] Implement max-depth option parsing
- [ ] Implement connection path query
- [ ] Add path visualization logic
- [ ] Add output formatting

### Clusters Command
- [ ] Implement min-size option parsing
- [ ] Implement file clustering algorithm
- [ ] Implement cluster query
- [ ] Add output formatting

### Custom Command
- [ ] Implement cypher-query argument handling
- [ ] Implement parameter parsing from key=value format
- [ ] Implement query execution
- [ ] Add output formatting

### Visualize Command
- [ ] Implement directory argument handling
- [ ] Implement visualization type option parsing
- [ ] Implement output format option parsing
- [ ] Implement visualization data generation
- [ ] Implement HTML template generation
- [ ] Implement browser opening logic

### Run Command
- [ ] Implement directory argument handling
- [ ] Implement exclude/include pattern parsing
- [ ] Implement skip flag handling
- [ ] Implement Neo4j Docker container management
- [ ] Implement full workflow execution
- [ ] Add progress reporting with spinners
- [ ] Implement error handling and recovery

## Example CLI Usage

```bash
# Run analysis on the current directory
codex-arch analyze

# Find direct dependencies of a file
codex-arch query dependencies src/index.ts

# Find files that import a specific file
codex-arch query dependencies src/utils/helpers.ts --reverse

# Find most imported files
codex-arch query most-imported --limit 10

# Find connection between two files
codex-arch query connection src/components/Button.tsx src/pages/Home.tsx

# Generate visualization
codex-arch visualize --type dependency-graph

# Run the complete workflow
codex-arch run --exclude node_modules dist
```

## CLI Command Mapping from Existing Scripts

| Current Script Function | CLI Command | Purpose |
|-------------------------|-------------|---------|
| `queryDirectDependencies` | `codex-arch query dependencies <file-path>` | Find direct dependencies |
| `queryReverseDependencies` | `codex-arch query dependencies <file-path> --reverse` | Find reverse dependencies |
| `queryMostImportedFiles` | `codex-arch query most-imported --limit <number>` | Find most imported files |
| `queryDependencyChains` | `codex-arch query dependencies <file-path> --depth <number>` | Find dependency chains |
| `queryIsolatedFiles` | `codex-arch query isolated` | Find isolated files |
| `queryFileClustering` | `codex-arch query clusters` | Find file clusters |
| `queryDependencyGraph` | `codex-arch query dependencies <file-path> --depth <number> --format tree` | View dependency tree |
| `queryReverseDependencyChain` | `codex-arch query dependencies <file-path> --reverse --depth <number>` | Find reverse dependency chains |
| `queryConnectionPath` | `codex-arch query connection <file1> <file2>` | Find connection between files |
| All analysis and visualization | `codex-arch run <directory>` | Run complete workflow |

## Output Directory Structure

The CLI should maintain the same output directory structure as the current scripts:

```
outputs/
├── typescript/                        # TypeScript analysis files
│   └── typescript-analysis-*.json     # Analysis output files
└── visualizations/                    # Visualization files
    ├── typescript-visualization.html  # HTML visualization
    ├── dependency-graph.json          # Dependency graph data
    └── cluster-graph.json             # Cluster graph data
```

These directories should be created automatically if they don't exist, and should be the default output locations. Users should be able to specify alternative locations via command options. 