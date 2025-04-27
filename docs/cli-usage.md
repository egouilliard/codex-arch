# CLI Usage

This document describes the Command Line Interface (CLI) for Codex-Arch, which provides direct access to the tool's capabilities.

## Installation

```bash
# Global installation
npm install -g codex-arch

# Local installation
npm install codex-arch
```

## Commands

### analyze

Analyzes a codebase and builds a knowledge graph.

```bash
codex-arch analyze <directory> [options]
```

**Arguments:**
- `directory`: Directory to analyze

**Options:**
- `-e, --exclude <patterns>`: Patterns to exclude (e.g., `node_modules/**,dist/**`)
- `-i, --include <patterns>`: Patterns to include (e.g., `*.ts,*.js`)
- `-d, --depth <number>`: Maximum directory depth (default: unlimited)
- `-c, --config <file>`: Path to configuration file

**Example:**
```bash
codex-arch analyze ./src --exclude "node_modules/**,dist/**" --include "*.ts"
```

### query

Queries the knowledge graph for information.

```bash
codex-arch query <query-type> [options]
```

**Query Types:**
- `file`: Query file information
- `function`: Query function information
- `relationship`: Query relationships between entities
- `context`: Query contextual information

**Options:**
- `-p, --path <path>`: Path to entity
- `-n, --name <name>`: Name of entity
- `-t, --type <type>`: Type of relationship
- `-d, --depth <number>`: Depth of relationships to traverse
- `-l, --limit <number>`: Limit number of results
- `-f, --format <format>`: Output format (json, table, text)

**Examples:**
```bash
codex-arch query file --path "./src/index.ts"
codex-arch query function --path "./src/utils.ts" --name "parseConfig"
codex-arch query relationship --path "./src/components/Button.tsx" --type "imports" --depth 2
```

### visualize

Generates a visualization of the codebase architecture.

```bash
codex-arch visualize [options]
```

**Options:**
- `-o, --output <file>`: Output file path
- `-f, --format <format>`: Output format (svg, html, json)
- `-r, --root <path>`: Root directory or file
- `-d, --depth <number>`: Depth of relationships to include
- `-t, --types <types>`: Relationship types to include

**Example:**
```bash
codex-arch visualize --output "./architecture.svg" --root "./src" --depth 3
```

### context

Manages project-specific contextual information.

```bash
codex-arch context <action> [options]
```

**Actions:**
- `add`: Add contextual information
- `get`: Retrieve contextual information
- `list`: List all contextual information
- `remove`: Remove contextual information

**Options:**
- `-k, --key <key>`: Context key
- `-v, --value <value>`: Context value
- `-c, --category <category>`: Context category

**Examples:**
```bash
codex-arch context add --key "primaryColor" --value "#3366FF" --category "design"
codex-arch context get --category "design"
```

## Configuration File

Codex-Arch can be configured using a `.codexarchrc.json` file:

```json
{
  "include": ["*.ts", "*.js"],
  "exclude": ["node_modules/**", "dist/**"],
  "parser": {
    "typescript": {
      "parseJSDoc": true
    }
  },
  "graph": {
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "user": "neo4j",
      "password": "password"
    }
  }
}
```

## Environment Variables

The CLI respects the following environment variables:

- `CODEX_ARCH_NEO4J_URI`: Neo4j database URI
- `CODEX_ARCH_NEO4J_USER`: Neo4j username
- `CODEX_ARCH_NEO4J_PASSWORD`: Neo4j password
- `CODEX_ARCH_GOOGLE_API_KEY`: Google API key for LLM integration

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Configuration error
- `3`: Parser error
- `4`: Graph error