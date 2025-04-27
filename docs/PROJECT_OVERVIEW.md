# Codex-Arch: Project Overview

Codex-Arch is a comprehensive codebase architecture analysis tool that builds a knowledge graph of code relationships, optimized for AI agent integration through MCP (Model Context Protocol).

## Purpose and Goals

Codex-Arch aims to help developers and AI systems:
- Understand codebases quickly by analyzing relationships between files and components
- Navigate complex projects by visualizing dependencies and interactions
- Extract semantic information about functions, classes, and other code entities
- Store and retrieve contextual information about project standards and best practices
- Integrate with AI agents (like Cursor) to enable intelligent code navigation and understanding

## Core Components

### 1. Graph Engine
- Integration with Graphiti for knowledge graph construction
- Custom schema definition for code entities and relationships
- Temporal tracking of code changes
- Query optimization for code relationship traversal
- Strategies for handling large codebases through partitioning and lazy loading

### 2. Code Analysis System
- Language-agnostic parser interfaces with initial focus on TypeScript/JavaScript and Python
- AST (Abstract Syntax Tree) processing
- Relationship extraction for imports, function calls, class inheritance, component composition
- Semantic analysis of code structures using Gemini LLM

### 3. MCP Protocol Layer
- Standardized actions mirroring CLI capabilities
- Response formatting optimized for LLM consumption
- Context window management for large codebases
- Streaming capabilities for progressive information delivery

### 4. Visualization Module
- Tiered visualization approach (simple to complex)
- Graph rendering interfaces with focus on clarity
- Export capabilities for various formats
- Interactive exploration capabilities

### 5. Context Management
- Storage for project-specific information
- Tagging and categorization system
- Integration with documentation
- Best practices and standards tracking

## Project Structure
```text
.
├── README.md
├── docker
│   ├── docker-compose.yml
│   └── neo4j
├── docs
│   └── PROJECT_OVERVIEW.md
├── lerna.json
├── package.json
├── packages
│   ├── cli
│   │   ├── package.json
│   │   ├── src
│   │   │   └── index.ts
│   │   ├── tests
│   │   └── tsconfig.json
│   ├── core
│   │   ├── package.json
│   │   ├── src
│   │   │   ├── graph
│   │   │   │   └── graphiti-client.ts
│   │   │   ├── index.ts
│   │   │   ├── mcp
│   │   │   ├── models
│   │   │   ├── parsers
│   │   │   │   └── parser-interface.ts
│   │   │   └── utils
│   │   ├── tests
│   │   └── tsconfig.json
│   ├── mcp
│   │   ├── package.json
│   │   ├── src
│   │   │   ├── actions.ts
│   │   │   └── index.ts
│   │   ├── tests
│   │   └── tsconfig.json
│   └── parsers-typescript
│       ├── package.json
│       ├── src
│       │   ├── index.ts
│       │   └── typescript-parser.ts
│       ├── tests
│       └── tsconfig.json
└── tsconfig.json
```


## Development Roadmap

### Phase 1: Foundation (3 weeks)
1. **Core Infrastructure**
   - Set up project structure and package configurations
   - Implement Neo4j and Graphiti integration
   - Create parser framework
   - Implement basic CLI

2. **Knowledge Graph Schema**
   - Define entity types (files, functions, classes, etc.)
   - Design relationship types
   - Implement Neo4j constraints and indices

3. **Basic Parser Implementation**
   - Create TypeScript parser for basic entities
   - Implement relationship extraction
   - Add AST traversal for code analysis

### Phase 2: MCP and Analysis Enhancement (3 weeks)
1. **MCP Protocol Implementation**
   - Design action interfaces
   - Implement response formatting
   - Build query optimization for LLMs

2. **Advanced Code Analysis**
   - Add function signature analysis
   - Implement dependency tracking
   - Create call graph construction

3. **Python Parser**
   - Implement Python AST parsing
   - Add Python-specific relationship extraction
   - Create cross-language relationships

### Phase 3: Visualization and Integration (2 weeks)
1. **Visualization Implementation**
   - Create graph visualization exports
   - Implement interactive views
   - Add filtering and search capabilities

2. **Tool Integration**
   - Implement Cursor integration
   - Add IDE plugin support
   - Create API for other tooling

### Phase 4: Refinement and Testing (2 weeks)
1. **Performance Optimization**
   - Optimize for large codebases
   - Implement caching strategies
   - Enhance query performance

2. **Testing and Documentation**
   - Create comprehensive tests
   - Write documentation
   - Develop examples and tutorials

## Links to Detailed Documentation
- [Knowledge Graph Schema](./docs/KNOWLEDGE_GRAPH.md)
- [Graphiti Integration](./docs/GRAPHITI.md)
- [MCP Implementation](./docs/MCP.md)
- [Parser Design](./docs/PARSERS.md)
- [CLI Usage](./docs/CLI.md)