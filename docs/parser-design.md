# Parser Design

This document outlines the parser architecture in Codex-Arch, which is responsible for analyzing code and extracting entities and relationships.

## Overview

The parser system in Codex-Arch follows a plugin-based architecture, allowing for language-specific implementations while maintaining a consistent interface. It extracts code entities (files, functions, classes, etc.) and their relationships from source code.

## Parser Interface

All language-specific parsers implement the common interface defined in `packages/core/src/parsers/parser-interface.ts`, which includes:

```typescript
export interface Parser {
  initialize(options?: ParserOptions): Promise<void>;
  parseFile(filePath: string): Promise<ParseResult>;
  parseDirectory(directoryPath: string): Promise<ParseResult>;
}

export interface ParseResult {
  entities: CodeEntity[];
  relationships: CodeRelationship[];
}
```

## Entity Types

Parsers extract the following types of entities:

- **Files**: Source code files
- **Functions**: Function declarations and expressions
- **Classes**: Class declarations
- **Variables**: Variable declarations
- **Imports**: Import statements
- **Components**: UI components (e.g., React components)

## Relationship Extraction

Parsers identify relationships between entities, including:

- Containment (file contains function)
- Imports (file imports another file)
- Function calls (function calls another function)
- Inheritance (class inherits from another class)
- Usage (function uses a variable)

## Language-Specific Parsers

### TypeScript Parser

Located in `packages/parsers-typescript`, this parser:
- Uses TypeScript Compiler API for AST traversal
- Handles JavaScript, TypeScript, JSX, and TSX files
- Extracts TypeScript-specific constructs (interfaces, types, etc.)

### Python Parser

Located in `packages/parsers-python`, this parser:
- Uses Python's AST module via a bridge
- Handles Python modules, classes, and functions
- Extracts Python-specific constructs (decorators, etc.)

## Parser Workflow

1. **Initialization**: Set up the parser with configuration options
2. **File Analysis**: Parse individual files to extract entities and relationships
3. **Directory Traversal**: Recursively analyze directories, respecting exclude patterns
4. **Entity Consolidation**: Combine entities and relationships from multiple files
5. **Graph Population**: Store the extracted information in the knowledge graph

## Configuration Options

Parsers accept the following configuration:

- **includePatterns**: File patterns to include (e.g., `["*.ts", "*.js"]`)
- **excludePatterns**: File patterns to exclude (e.g., `["node_modules/**"]`)
- **maxDepth**: Maximum recursion depth for directory traversal
- **parseComments**: Whether to parse comments for documentation

## Extension Points

The parser system is designed for extensibility:

- New language parsers can be added by implementing the Parser interface
- Custom entity types can be defined for language-specific constructs
- Additional relationship types can be introduced for specific paradigms

## Integration with LLM

For complex analysis, parsers can leverage LLM capabilities:

- Generating natural language descriptions of functions
- Inferring semantics from variable names and code patterns
- Identifying design patterns and architectural components