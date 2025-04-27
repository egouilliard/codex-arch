# Codex Arch

Codex Arch is a codebase architecture analysis tool that builds a knowledge graph of code relationships. It helps developers understand complex codebases by analyzing and visualizing code dependencies, relationships, and patterns.

## Features

- Parse TypeScript code to extract entities and relationships
- Build a Neo4j-based knowledge graph of your code
- Query the graph to discover insights and patterns
- Visualize code dependencies and relationships
- Extensible architecture for adding more language parsers

## Project Structure

Codex Arch is a TypeScript monorepo with the following packages:

- `@codex-arch/core`: Core functionality for knowledge graph operations
- `@codex-arch/parsers-typescript`: TypeScript parser implementation
- `@codex-arch/mcp`: Model Context Protocol implementation 
- `@codex-arch/cli`: Command-line interface

## Getting Started

### Prerequisites

- Node.js 14.x or higher
- Yarn
- Docker and Docker Compose (for Neo4j)

### Setting Up the Development Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/codex-arch.git
cd codex-arch
```

2. Install dependencies:

```bash
yarn install
```

3. Build the packages:

```bash
yarn build
```

4. Start Neo4j using Docker Compose:

```bash
cd docker
docker-compose up -d
```

5. Configure the CLI:

```bash
yarn cli config --uri bolt://localhost:7687 --username neo4j --password password
```

### Using the CLI

#### Analyze a codebase:

```bash
yarn cli analyze /path/to/your/codebase --exclude "node_modules" "dist"
```

#### Run a query against the knowledge graph:

```bash
yarn cli query "MATCH (n:Class) RETURN n.name, n.filePath"
```

## Architecture

Codex Arch uses a modular architecture:

1. **Parsers** analyze code and extract entities and relationships
2. **Core** provides graph operations and data models
3. **CLI** provides a command-line interface for users
4. **MCP** implements the Model Context Protocol for integration with other tools

The system stores data in a Neo4j graph database, which allows for powerful querying and visualization of code relationships.

## Contributing

Contributions are welcome! Please check out our contribution guidelines for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Neo4j for the graph database
- TypeScript team for the compiler API
- All contributors and supporters 