# Graphiti Query Documentation

This document provides details on all the query types available in Codex-Arch for analyzing codebases using the Neo4j-backed knowledge graph.

## Overview

Codex-Arch uses Neo4j's Cypher query language to extract valuable insights from the code structure. The queries range from simple file dependency lookups to complex architectural analyses.

## Available Query Types

### 1. Direct Dependencies

Identifies all files directly imported by a specific file.

#### Cypher Query
```cypher
MATCH (file:File {path: $filePath})-[r:IMPORTS]->(dependency:File)
RETURN dependency.path AS dependencyPath
```

#### Usage
```typescript
// Using GraphitiClient directly
const dependencies = await client.runQuery<{ dependencyPath: string }>(query, { filePath });

// Using the test-graphiti-queries.ts script
await queryDirectDependencies("path/to/file.ts");
```

#### Example Output
```
------ Direct Dependencies for src/components/App.tsx ------
1. src/utils/helpers.ts
2. src/types/index.ts
3. src/services/api.ts
4. src/hooks/useApi.ts
5. src/hooks/useForm.ts
6. src/components/common/Input.tsx
7. src/components/common/Button.tsx
8. src/components/common/Card.tsx
9. src/components/Footer.tsx
10. src/components/Header.tsx
Total: 10 direct dependencies
```

#### Interpretation
This shows all files that are directly imported by the target file. These represent immediate dependencies and the most direct architectural connections.

### 2. Reverse Dependencies

Identifies all files that import a specific file.

#### Cypher Query
```cypher
MATCH (file:File)-[r:IMPORTS]->(dependency:File {path: $filePath})
RETURN file.path AS importerPath
```

#### Usage
```typescript
// Using GraphitiClient directly
const importers = await client.runQuery<{ importerPath: string }>(query, { filePath });

// Using the test-graphiti-queries.ts script
await queryReverseDependencies("path/to/file.ts");
```

#### Example Output
```
------ Reverse Dependencies for src/types/index.ts ------
1. src/components/App.tsx
2. src/hooks/useForm.ts
3. src/hooks/useApi.ts
4. src/services/api.ts
5. src/services/auth.ts
Total: 5 reverse dependencies
```

#### Interpretation
This shows all files that directly import the target file. A high number of importers indicates that the file is a core component in the codebase, and changes could have wide-ranging impacts.

### 3. Most Imported Files

Identifies the most commonly imported files in the codebase.

#### Cypher Query
```cypher
MATCH (file:File)-[r:IMPORTS]->(dependency:File)
WITH dependency, COUNT(file) AS importCount
RETURN dependency.path AS filePath, importCount
ORDER BY importCount DESC
LIMIT $limit
```

#### Usage
```typescript
// Using GraphitiClient directly
const mostImported = await client.runQuery<{ filePath: string; importCount: number }>(query, { limit: 5 });

// Using the test-graphiti-queries.ts script
await queryMostImportedFiles(5);
```

#### Example Output
```
------ Top 5 Most Imported Files ------
1. src/types/index.ts - imported by 5 files
2. src/components/App.tsx - imported by 1 files
3. src/App.css - imported by 1 files
4. src/utils/validators.ts - imported by 1 files
5. src/components/common/Input.tsx - imported by 1 files
```

#### Interpretation
This identifies the most reused files in your codebase. These files represent:
1. Core utilities and shared components
2. Key abstractions that multiple parts of your system depend on
3. Potential architectural bottlenecks if they need to change

### 4. Dependency Chains

Traces all dependencies of a file to a specified depth.

#### Cypher Query
```cypher
MATCH p=(file:File {path: $filePath})-[r:IMPORTS*1..$depth]->(dependency:File)
WITH file, dependency, length(p) AS chainDepth
RETURN file.path AS source, dependency.path AS target, chainDepth AS depth
ORDER BY chainDepth
```

#### Usage
```typescript
// Using GraphitiClient directly
const chains = await client.runQuery<{ source: string; target: string; depth: number }>(query, { filePath, depth: 2 });

// Using the test-graphiti-queries.ts script
await queryDependencyChains("path/to/file.ts", 2);
```

#### Example Output
```
------ Dependency Chain for src/components/App.tsx (depth: 2) ------
Depth 1:
  1. src/components/Header.tsx
  2. src/components/Footer.tsx
  ...
  Total at depth 1: 10 files

Depth 2:
  1. src/services/auth.ts
  2. src/types/index.ts
  3. src/utils/validators.ts
  ...
  Total at depth 2: 5 files

Total dependencies in chain: 15 files
```

#### Interpretation
This shows the transitive dependency tree for the specified file. Files at deeper levels represent indirect dependencies that your file might be unaware of but still relies on for correct functionality.

### 5. Reverse Dependency Chain

Identifies files that directly or indirectly depend on a specific file.

#### Cypher Query
```cypher
MATCH p=(importer:File)-[r:IMPORTS*1..$depth]->(file:File {path: $filePath})
WITH importer, file, length(p) AS chainDepth
RETURN importer.path AS source, file.path AS target, chainDepth AS depth
ORDER BY chainDepth
```

#### Usage
```typescript
// Using GraphitiClient directly
const reverseChains = await client.runQuery<{ source: string; target: string; depth: number }>(query, { filePath, depth: 2 });

// Using the test-graphiti-queries.ts script
await queryReverseDependencyChain("path/to/file.ts", 2);
```

#### Example Output
```
------ Reverse Dependency Chain for src/types/index.ts (depth: 2) ------
Depth 1:
  1. src/components/App.tsx
  2. src/hooks/useForm.ts
  ...
  Total at depth 1: 5 files

Depth 2:
  1. src/index.tsx
  ...
  Total at depth 2: 1 files

Total reverse dependencies: 6 files
```

#### Interpretation
This shows the "reverse impact radius" of a file. Files at depth 1 directly import the target file, while files at depth 2 import those importers. This indicates the potential impact of changes to the target file across the codebase.

### 6. Isolated Files

Identifies files that neither import other files nor are imported by others.

#### Cypher Query
```cypher
MATCH (file:File)
WHERE NOT (file)-[:IMPORTS]->() AND NOT ()-[:IMPORTS]->(file)
RETURN file.path AS filePath
```

#### Usage
```typescript
// Using GraphitiClient directly
const isolated = await client.runQuery<{ filePath: string }>(query);

// Using the test-graphiti-queries.ts script
await queryIsolatedFiles();
```

#### Example Output
```
------ Isolated Files ------
1. src/types/models.ts
Total: 1 isolated files
```

#### Interpretation
These files are not connected to the rest of your codebase:
1. They might be unused and candidates for removal
2. They could be entry points like main.ts files
3. They might represent issues with your import analysis

### 7. Directory Clustering Analysis

Groups files by directory and analyzes inter-directory connections.

#### Cypher Query
```cypher
// Directory structure
MATCH (file:File)
WITH split(file.path, '/') AS parts
WITH parts[size(parts)-2] AS directory, count(*) AS fileCount
WHERE directory IS NOT NULL
RETURN directory, fileCount
ORDER BY fileCount DESC
LIMIT 10

// Directory connections
MATCH (f1:File)-[:IMPORTS]->(f2:File)
WITH split(f1.path, '/') AS parts1, split(f2.path, '/') AS parts2
WITH parts1[size(parts1)-2] AS dir1, parts2[size(parts2)-2] AS dir2
WHERE dir1 <> dir2 AND dir1 IS NOT NULL AND dir2 IS NOT NULL
RETURN dir1, dir2, count(*) AS connections
ORDER BY connections DESC
LIMIT 10
```

#### Usage
```typescript
// Using the test-graphiti-queries.ts script
await queryFileClustering();
```

#### Example Output
```
------ Directory Clustering Analysis ------
Directory Structure:
1. common: 3 files
2. components: 3 files
3. src: 2 files
...

Directory Connections:
1. components → common: 3 connections
2. services → types: 2 connections
3. hooks → types: 2 connections
...
```

#### Interpretation
1. Directories with many files might indicate too much responsibility
2. High inter-directory connections suggest tight coupling
3. Consider refactoring directories with many outgoing connections

### 8. Connection Path Between Files

Finds if and how two files are connected, directly or indirectly.

#### Cypher Query
```cypher
// Direct connection check
MATCH p=(file1:File {path: $filePath1})-[r:IMPORTS]->(file2:File {path: $filePath2})
RETURN p

// Indirect connection check
MATCH p=shortestPath((file1:File {path: $filePath1})-[:IMPORTS*]->(file2:File {path: $filePath2}))
WHERE length(p) > 1
RETURN [node in nodes(p) | node.path] AS path, length(p) - 1 AS length
```

#### Usage
```typescript
// Using the test-graphiti-queries.ts script
await queryConnectionPath("path/to/file1.ts", "path/to/file2.ts", 4);
```

#### Example Output
```
------ Connection Path Between Two Files ------
File 1: src/index.tsx
File 2: src/services/auth.ts
Maximum path depth: 4

Results:
INDIRECT CONNECTION found with path length of 3 hops.

Simplified path:
index.tsx → App.tsx → Header.tsx → auth.ts

Detailed path:
src/index.tsx
imports ↓
src/components/App.tsx
imports ↓
src/components/Header.tsx
imports ↓
src/services/auth.ts

Connection distance: 3 hops
```

#### Interpretation
This shows how two files are connected through imports. The connection can be:
1. Direct (one file directly imports the other)
2. Indirect (connected through intermediate files)
3. Non-existent (no path exists between them)

Understanding these connections helps identify non-obvious dependencies and potential impacts of changes.

### 9. Dependency Graph Visualization

Generates a text-based visualization of the dependency graph for a file.

#### Cypher Query
```cypher
MATCH path = (file:File {path: $filePath})-[r:IMPORTS*1..$depth]->(dependency:File)
RETURN path
```

#### Usage
```typescript
// Using the test-graphiti-queries.ts script
await queryDependencyGraph("path/to/file.ts", 2);
```

#### Example Output
```
------ Dependency Graph for src/components/App.tsx (depth: 2) ------
App.tsx
  ├─ Header.tsx
  │    └─ auth.ts
  ├─ Footer.tsx
  ├─ Card.tsx
  ├─ Button.tsx
  ├─ Input.tsx
  ├─ useForm.ts
  │    ├─ index.ts
  │    └─ validators.ts
  ...
```

#### Interpretation
This tree shows the dependency hierarchy starting from the given file. Each level represents direct imports and their subsequent imports, providing a visual representation of the dependency structure.

## Extending Queries

You can extend these queries for different use cases by:

### Modifying Depth Parameters

Increase or decrease the depth parameter to control how far the query traverses:

```typescript
// Shallow analysis (direct dependencies only)
await queryDependencyChains(filePath, 1);

// Deep analysis (up to 5 levels deep)
await queryDependencyChains(filePath, 5);
```

### Adding Filters

Add WHERE clauses to filter results based on specific criteria:

```cypher
// Only TypeScript files
MATCH (file:File)-[r:IMPORTS]->(dependency:File)
WHERE dependency.path ENDS WITH '.ts'
RETURN file.path, dependency.path

// Excluding test files
MATCH (file:File)-[r:IMPORTS]->(dependency:File)
WHERE NOT dependency.path CONTAINS 'test' AND NOT dependency.path CONTAINS 'spec'
RETURN file.path, dependency.path
```

### Adding Additional Relationship Types

As your schema evolves to include more relationship types, you can modify queries to include them:

```cypher
// Include CALLS relationships
MATCH (file1:File)-[:IMPORTS|CALLS]->(file2:File)
RETURN file1.path, file2.path, type(r) AS relationshipType
```

### Combining Queries

Combine multiple query types for more complex analysis:

```cypher
// Find files that are both heavily imported and also have many dependencies
MATCH (file:File)
OPTIONAL MATCH (importer:File)-[:IMPORTS]->(file)
WITH file, COUNT(importer) AS importCount
OPTIONAL MATCH (file)-[:IMPORTS]->(dependency:File)
WITH file, importCount, COUNT(dependency) AS dependencyCount
WHERE importCount > 0 AND dependencyCount > 0
RETURN file.path, importCount, dependencyCount
ORDER BY (importCount + dependencyCount) DESC
LIMIT 10
```

## Performance Considerations

1. **Limit Query Depth**: Deep traversals (depth > 4) can be resource-intensive
2. **Use Appropriate Indices**: Ensure paths and other key properties are indexed
3. **Limit Results**: Use LIMIT to cap result sets for large codebases
4. **WHERE Clauses First**: Place filtering WHERE clauses early in your query for better performance

## Command Line Usage

You can run these queries directly from the CLI:

```bash
# Run a specific query
npm run graphiti:query "MATCH (f:File) RETURN count(f) as fileCount"

# Run the comprehensive query test suite
npm run graphiti:test-queries

# Generate visualization
npm run graphiti:html
``` 