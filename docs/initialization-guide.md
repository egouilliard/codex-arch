# Codex-Arch Initialization Guide

This guide provides instructions for setting up and initializing the Codex-Arch project.

## Project Initialization

To initialize the project, provide this prompt to Cursor or another AI assistant:

```
I want to initialize a new project called "codex-arch" which will be a codebase architecture analysis tool that builds a knowledge graph of code relationships.

Please help me:

1. Set up a TypeScript monorepo structure using Lerna and Yarn workspaces with the following packages:
   - @codex-arch/core: Core functionality for knowledge graph operations
   - @codex-arch/parsers-typescript: TypeScript parser implementation
   - @codex-arch/mcp: Model Context Protocol implementation
   - @codex-arch/cli: Command-line interface

2. Create the following directory structure:
   ```
   codex-arch/
   ├── packages/
   │   ├── core/
   │   │   ├── src/
   │   │   │   ├── graph/
   │   │   │   ├── parsers/
   │   │   │   ├── models/
   │   │   │   ├── mcp/
   │   │   │   └── utils/
   │   │   ├── tests/
   │   │   ├── package.json
   │   │   └── tsconfig.json
   │   ├── parsers-typescript/
   │   │   ├── src/
   │   │   ├── tests/
   │   │   ├── package.json
   │   │   └── tsconfig.json
   │   ├── mcp/
   │   │   ├── src/
   │   │   ├── tests/
   │   │   ├── package.json
   │   │   └── tsconfig.json
   │   └── cli/
   │       ├── src/
   │       ├── tests/
   │       ├── package.json
   │       └── tsconfig.json
   ├── docker/
   │   ├── neo4j/
   │   └── docker-compose.yml
   ├── docs/
   ├── package.json
   ├── lerna.json
   ├── tsconfig.json
   └── README.md
   ```

3. Configure package.json files with appropriate dependencies:
   - Root package: lerna, typescript, prettier, eslint
   - @codex-arch/core: neo4j-driver, @google-ai/generativelanguage
   - @codex-arch/parsers-typescript: typescript (compiler API)
   - @codex-arch/mcp: express (or other server framework)
   - @codex-arch/cli: commander, chalk

4. Set up TypeScript configurations for each package with paths to enable proper imports

5. Create the following initial files:
   - packages/core/src/graph/graphiti-client.ts: Class for Neo4j/Graphiti integration
   - packages/core/src/parsers/parser-interface.ts: Interface for language parsers
   - packages/parsers-typescript/src/typescript-parser.ts: Basic implementation
   - packages/mcp/src/actions.ts: MCP actions definition
   - packages/cli/src/index.ts: CLI entry point

6. Set up a docker-compose.yml for Neo4j with appropriate volumes and ports

7. Create a basic README.md that explains:
   - What codex-arch is and its purpose
   - How to set up the development environment
   - How to use the CLI

Please initialize all the basic files with placeholder implementations so we can fill in the details later.
```

## Development Environment Setup

After initializing the project structure:

1. **Install Dependencies**
   ```bash
   yarn install
   ```

2. **Start Neo4j**
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Build the Project**
   ```bash
   yarn build
   ```

4. **Run Development CLI**
   ```bash
   cd packages/cli
   yarn dev analyze ./path/to/codebase
   ```

## Configuration

1. **Environment Variables**

   Create a `.env` file in the project root:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   GOOGLE_API_KEY=your_api_key
   ```

2. **Google API Key**

   To use the Gemini LLM features, [obtain a Google API key](https://ai.google.dev/) and set it in your environment variables.

## Next Steps

After initialization:

1. **Implement Core Components**
   - Complete the GraphitiClient implementation
   - Finalize the parser interface
   - Set up Neo4j schema

2. **Develop TypeScript Parser**
   - Implement AST traversal
   - Add relationship detection
   - Integrate with the graph client

3. **Build MCP Protocol Layer**
   - Implement action handlers
   - Create server implementation
   - Add authentication

4. **Create CLI Commands**
   - Implement analyze, query, and visualize commands
   - Add configuration management
   - Develop user interface