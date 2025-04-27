# Knowledge Graph Schema

This document defines the knowledge graph schema used in Codex-Arch to represent code entities and their relationships.

## Entity Types

### File
- **Properties**:
  - `path`: string (unique identifier)
  - `name`: string
  - `extension`: string
  - `size`: number
  - `lastModified`: datetime

### Function
- **Properties**:
  - `name`: string
  - `signature`: string
  - `returnType`: string
  - `documentation`: string
  - `startLine`: number
  - `endLine`: number

### Class
- **Properties**:
  - `name`: string
  - `documentation`: string
  - `startLine`: number
  - `endLine`: number

### Variable
- **Properties**:
  - `name`: string
  - `type`: string
  - `constant`: boolean
  - `value`: string (if literal)
  - `startLine`: number

### Import
- **Properties**:
  - `source`: string
  - `importType`: string (named, default, namespace, etc.)
  - `startLine`: number

### Component
- **Properties**:
  - `name`: string
  - `type`: string (functional, class)
  - `startLine`: number
  - `endLine`: number

### ProjectContext
- **Properties**:
  - `key`: string
  - `value`: string
  - `category`: string
  - `timestamp`: datetime

## Relationship Types

### CONTAINS
- File CONTAINS Function
- File CONTAINS Class
- File CONTAINS Variable
- File CONTAINS Import
- File CONTAINS Component
- Class CONTAINS Function
- Class CONTAINS Variable

### IMPORTS
- File IMPORTS File
- Function IMPORTS Function

### CALLS
- Function CALLS Function

### INHERITS_FROM
- Class INHERITS_FROM Class

### IMPLEMENTS
- Class IMPLEMENTS Interface

### USES
- Function USES Variable
- Component USES Component

### REFERENCES
- Any entity REFERENCES any entity

### HAS_CONTEXT
- Any entity HAS_CONTEXT ProjectContext

## Indices and Constraints

- Unique constraint on File.path
- Index on Function.signature
- Index on Class.name
- Index on Import.source
- Index on Variable.name

## Temporal Tracking

Each entity and relationship includes:

- `createdAt`: When the entity/relationship was first observed
- `updatedAt`: When the entity/relationship was last updated
- `version`: Version identifier for tracking changes

## Schema Evolution

The schema is designed to be extensible:

- New entity types can be added as needed
- Additional properties can be added to existing entities
- New relationship types can be defined for specific languages

## Language-Specific Extensions

### TypeScript/JavaScript
- Additional properties for TypeScript-specific features
- Special handling for JSX/TSX components

### Python
- Support for Python-specific constructs (decorators, etc.)
- Module-level variables and functions