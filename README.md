# Codex-Arch

A code architecture analysis tool that parses source code and builds a graph representation.

## Features

- Parse TypeScript/JavaScript code
- Extract code entities and relationships
- Store the data in a Neo4j graph database
- Export analysis results as JSON
- Visualize code architecture and dependencies

## Project Structure

The project follows a monorepo structure using Lerna and Yarn workspaces.

- `packages/core`: Core entities and interfaces
- `packages/parsers-typescript`: TypeScript/JavaScript parser
- `packages/cli`: Command-line interface
- `packages/mcp`: Model-Controller-Provider architecture

## Installation

1. Clone the repository
2. Install dependencies:

```bash
yarn install
```

3. Build the packages:

```bash
yarn build
```

## Usage

### Analyzing a TypeScript/JavaScript Project

```bash
# Using the compiled CLI
node packages/cli/dist/index.js analyze ./path/to/repo --output ./outputs/typescript/typescript-analysis-reponame-$(date +%Y-%m-%d).json --include "**/*.ts,**/*.tsx,**/*.js,**/*.jsx" --exclude "**/node_modules/**"
```

### Analysis Output Organization

Analysis outputs are stored in the `outputs/` directory, organized by language:

- `outputs/typescript/`: TypeScript/JavaScript analysis outputs
- `outputs/python/`: Python analysis outputs
- `outputs/java/`: Java analysis outputs

See the [outputs README](./outputs/README.md) for more details on file naming conventions and usage.

## Development

### Building the Project

```bash
# Build all packages
yarn build

# Build a specific package
yarn workspace @codex-arch/core build
```

### Running Tests

```bash
# Run all tests
yarn test

# Run tests for a specific package
yarn workspace @codex-arch/core test
```

## License

MIT 