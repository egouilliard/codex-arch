# Graphiti Integration

This document outlines the integration of Graphiti in Codex-Arch, including setup, configuration, and implementation details.

## Overview

Graphiti is an open-source framework for building and querying dynamic, temporally-aware knowledge graphs. In Codex-Arch, we leverage Graphiti to represent relationships between code entities over time, enabling powerful querying capabilities.

## Key Features Used

- **Knowledge Graph Construction**: Graphiti provides the foundation for our knowledge graph, with support for complex relationships and temporal metadata.
- **Entity and Relationship Management**: We use Graphiti's entity and relationship models to represent code structures.
- **Semantic Search**: Graphiti's search capabilities allow us to perform both exact and semantic searches across the codebase.
- **Embedding Integration**: We utilize Gemini LLM for generating embeddings of code entities for semantic similarity.

## Implementation Details

### Neo4j Setup

Codex-Arch uses Neo4j as the backend database for the knowledge graph. The configuration is defined in `docker/docker-compose.yml`.

### GraphitiClient

The `GraphitiClient` class in `packages/core/src/graph/graphiti-client.ts` is our primary interface to Graphiti. It handles:

- Database connection management
- Schema initialization
- Node and relationship CRUD operations
- Search and query capabilities

### Schema Design

Our Neo4j schema includes:

- **Nodes**: Represent code entities (files, functions, classes, etc.)
- **Relationships**: Represent connections between entities (imports, calls, inherits, etc.)
- **Properties**: Store metadata about entities and relationships
- **Indices**: Optimize common query patterns
- **Constraints**: Ensure data integrity

### LLM Integration

We use Google's Gemini for:

- Generating embeddings for semantic search
- Creating natural language descriptions of code functions
- Extracting intent and relationships from code

## Configuration

The Graphiti integration can be configured through environment variables:

- `NEO4J_URI`: URI for the Neo4j database (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `password`)
- `GOOGLE_API_KEY`: API key for Google Gemini

## Usage in Codebase

The GraphitiClient is used by:

1. **Parsers**: To store extracted code entities and relationships
2. **MCP Protocol Layer**: To retrieve information in response to queries
3. **CLI Commands**: To perform analysis and query operations

## Initialization Process

1. Connection to Neo4j database
2. Creation of schema constraints and indices
3. Initialization of LLM client for embeddings
4. Configuration of search parameters

## Query Capabilities

Through Graphiti, Codex-Arch supports:

- Finding dependencies between files
- Identifying function call graphs
- Discovering class hierarchies
- Semantic search for related code structures
- Time-based queries showing the evolution of code