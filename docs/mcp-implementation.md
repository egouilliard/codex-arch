# MCP Implementation

This document outlines the Model Context Protocol (MCP) implementation in Codex-Arch, which allows AI agents to interact with the tool.

## Overview

MCP (Model Context Protocol) is a standardized way for AI systems to connect to external tools and services. In Codex-Arch, we implement MCP to enable AI agents like Cursor to query and understand codebases.

## Actions

The MCP implementation provides the following actions:

### `queryFile`
- **Description**: Get details about a specific file
- **Parameters**:
  - `path`: Path to the file
- **Returns**: File details, contained entities, and relationships

### `queryFunction`
- **Description**: Get function details and documentation
- **Parameters**:
  - `path`: Path to the file
  - `name`: Function name
- **Returns**: Function signature, documentation, and relationships

### `queryRelationships`
- **Description**: Find file/function dependencies
- **Parameters**:
  - `path`: Path to the file or function
  - `type`: Relationship type (imports, calls, etc.)
  - `depth`: Depth of relationships to retrieve
- **Returns**: List of related entities and their relationships

### `queryPath`
- **Description**: Find path between two files/functions
- **Parameters**:
  - `sourcePath`: Source path
  - `targetPath`: Target path
  - `relationshipTypes`: Types of relationships to consider
- **Returns**: Path between the entities

### `visualizeGraph`
- **Description**: Generate graph visualization for a set of files
- **Parameters**:
  - `paths`: Paths to the files
  - `relationships`: Relationship types to include
- **Returns**: Visualization data (SVG, JSON, etc.)

### `storeContext`
- **Description**: Store project-specific information
- **Parameters**:
  - `key`: Context key
  - `value`: Context value
  - `category`: Context category
- **Returns**: Confirmation of storage

### `retrieveContext`
- **Description**: Get stored contextual information
- **Parameters**:
  - `key`: Context key (optional)
  - `category`: Context category (optional)
- **Returns**: Matching contextual information

## Response Format

All MCP responses follow a consistent structure:

```json
{
  "result": {
    // Action-specific result data
  },
  "metadata": {
    "executionTime": "123ms",
    "nodeCount": 5,
    "relationshipCount": 10
  }
}
```

## Implementation Details

### Server

The MCP server is implemented in `packages/mcp/src/server.ts`, which:
- Registers all available actions
- Handles incoming requests
- Routes requests to the appropriate handler
- Formats responses for AI consumption

### Action Handlers

Each action has a handler function that:
- Validates input parameters
- Executes the requested operation
- Formats the result for the response

### Integration with Core

The MCP layer integrates with the core Codex-Arch functionality:
- Uses the graph client for knowledge graph queries
- Accesses parser capabilities for code understanding
- Leverages visualization components for graph rendering

## Usage in AI Agents

AI agents can use the MCP interface to:
- Understand code structure and organization
- Answer questions about dependencies and relationships
- Generate visualizations of code architecture
- Store and retrieve contextual information

## Error Handling

The MCP implementation includes robust error handling:
- Parameter validation with helpful error messages
- Graceful handling of not-found conditions
- Detailed error responses for debugging