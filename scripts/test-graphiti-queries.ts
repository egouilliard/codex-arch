import { GraphitiClient } from '../packages/core/src';
import { Record as Neo4jRecord } from 'neo4j-driver';

/**
 * TestGraphitiQueries - A class to demonstrate various query patterns with GraphitiClient
 * for extracting insights from a TypeScript repository's code structure.
 */
class TestGraphitiQueries {
  private client: GraphitiClient;

  /**
   * Initialize a new TestGraphitiQueries instance with Neo4j connection details
   * @param uri - The Neo4j server URI
   * @param username - Neo4j database username
   * @param password - Neo4j database password
   * @param database - Optional name of the database to connect to
   */
  constructor(
    uri: string = 'bolt://localhost:7687',
    username: string = 'neo4j',
    password: string = 'password',
    database?: string
  ) {
    this.client = new GraphitiClient({
      uri,
      username,
      password,
      database
    });
  }

  /**
   * Queries all files directly imported by a specified file
   * @param filePath - The path of the file to find imports for
   */
  async queryDirectDependencies(filePath: string): Promise<void> {
    console.log(`\n------ Direct Dependencies for ${filePath} ------`);
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH (file:File {path: "${filePath}"})-[r:IMPORTS]->(dependency:File)
RETURN dependency.path
    `);
    
    try {
      const query = `
        MATCH (file:File {path: $filePath})-[r:IMPORTS]->(dependency:File)
        RETURN dependency.path AS dependencyPath
      `;
      
      const result = await this.client.runQuery<{ dependencyPath: string }>(query, { filePath });
      const dependencies = result.map(record => record.dependencyPath);
      
      console.log('Results:');
      if (dependencies.length === 0) {
        console.log('No direct dependencies found');
      } else {
        dependencies.forEach((dep: string, idx: number) => {
          console.log(`${idx + 1}. ${dep}`);
        });
        console.log(`Total: ${dependencies.length} direct dependencies`);
      }
      
      console.log('Interpretation:');
      console.log(`The file "${filePath}" directly imports ${dependencies.length} other files.`);
    } catch (error) {
      console.error('Error querying direct dependencies:', error);
    }
  }

  /**
   * Queries all files that import a specified file (reverse dependencies)
   * @param filePath - The path of the file to find importers for
   */
  async queryReverseDependencies(filePath: string): Promise<void> {
    console.log(`\n------ Reverse Dependencies for ${filePath} ------`);
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH (file:File)-[r:IMPORTS]->(dependency:File {path: "${filePath}"})
RETURN file.path
    `);
    
    try {
      const query = `
        MATCH (file:File)-[r:IMPORTS]->(dependency:File {path: $filePath})
        RETURN file.path AS importerPath
      `;
      
      const result = await this.client.runQuery<{ importerPath: string }>(query, { filePath });
      const importers = result.map(record => record.importerPath);
      
      console.log('Results:');
      if (importers.length === 0) {
        console.log('No reverse dependencies found');
      } else {
        importers.forEach((imp: string, idx: number) => {
          console.log(`${idx + 1}. ${imp}`);
        });
        console.log(`Total: ${importers.length} reverse dependencies`);
      }
      
      console.log('Interpretation:');
      console.log(`The file "${filePath}" is imported by ${importers.length} other files.`);
    } catch (error) {
      console.error('Error querying reverse dependencies:', error);
    }
  }

  /**
   * Queries the most imported files in the codebase
   * @param limit - Number of top files to return
   */
  async queryMostImportedFiles(limit: number = 5): Promise<void> {
    console.log(`\n------ Top ${limit} Most Imported Files ------`);
    
    // Make sure limit is an integer
    const intLimit = Math.floor(limit);
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH (file:File)-[r:IMPORTS]->(dependency:File)
WITH dependency, COUNT(file) AS importCount
RETURN dependency.path, importCount
ORDER BY importCount DESC
LIMIT ${intLimit}
    `);
    
    try {
      const query = `
        MATCH (file:File)-[r:IMPORTS]->(dependency:File)
        WITH dependency, COUNT(file) AS importCount
        RETURN dependency.path AS filePath, importCount
        ORDER BY importCount DESC
        LIMIT toInteger($limit)
      `;
      
      const result = await this.client.runQuery<{ filePath: string; importCount: any }>(query, { limit: intLimit });
      const mostImported = result.map(record => ({
        path: record.filePath,
        count: typeof record.importCount === 'number' ? record.importCount : parseInt(record.importCount.toString())
      }));
      
      console.log('Results:');
      if (mostImported.length === 0) {
        console.log('No imports found in the codebase');
      } else {
        mostImported.forEach((item: { path: string; count: number }, idx: number) => {
          console.log(`${idx + 1}. ${item.path} - imported by ${item.count} files`);
        });
      }
      
      console.log('Interpretation:');
      console.log('These are the most reused files in your codebase. They represent:');
      console.log('1. Core utilities and shared components');
      console.log('2. Key abstractions that multiple parts of your system depend on');
      console.log('3. Potential architectural bottlenecks if they need to change');
    } catch (error) {
      console.error('Error querying most imported files:', error);
    }
  }

  /**
   * Queries all files in the dependency chain of a file
   * @param filePath - The path of the file to find the dependency chain for
   * @param depth - Maximum depth for the dependency chain traversal
   */
  async queryDependencyChains(filePath: string, depth: number = 3): Promise<void> {
    console.log(`\n------ Dependency Chain for ${filePath} (depth: ${depth}) ------`);
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH p=(file:File {path: "${filePath}"})-[r:IMPORTS*1..${depth}]->(dependency:File)
WITH file, dependency, length(p) AS chainDepth
RETURN file.path AS source, dependency.path AS target, chainDepth
ORDER BY chainDepth
    `);
    
    try {
      const query = `
        MATCH p=(file:File {path: $filePath})-[r:IMPORTS*1..${depth}]->(dependency:File)
        WITH file, dependency, length(p) AS chainDepth
        RETURN file.path AS source, dependency.path AS target, chainDepth AS depth
        ORDER BY chainDepth
      `;
      
      const result = await this.client.runQuery<{ source: string; target: string; depth: any }>(query, { filePath });
      const chains = result.map(record => ({
        source: record.source,
        target: record.target,
        depth: typeof record.depth === 'number' ? record.depth : parseInt(record.depth.toString())
      }));
      
      console.log('Results:');
      if (chains.length === 0) {
        console.log('No dependency chains found');
      } else {
        const byDepth: { [key: number]: string[] } = {};
        
        chains.forEach((item: { source: string; target: string; depth: number }) => {
          if (!byDepth[item.depth]) {
            byDepth[item.depth] = [];
          }
          byDepth[item.depth].push(item.target);
        });
        
        Object.keys(byDepth).sort((a, b) => parseInt(a) - parseInt(b)).forEach(d => {
          const depthNum = parseInt(d);
          console.log(`\nDepth ${depthNum}:`);
          byDepth[depthNum].forEach((dep, idx) => {
            console.log(`  ${idx + 1}. ${dep}`);
          });
          console.log(`  Total at depth ${depthNum}: ${byDepth[depthNum].length} files`);
        });
        
        console.log(`\nTotal dependencies in chain: ${chains.length} files`);
      }
      
      console.log('Interpretation:');
      console.log(`This shows the transitive dependency tree for "${filePath}".`);
      console.log('Files at deeper levels represent indirect dependencies that your file');
      console.log('might be unaware of but still relies on for correct functionality.');
    } catch (error) {
      console.error('Error querying dependency chains:', error);
    }
  }

  /**
   * Queries files that are isolated (no imports or importers)
   */
  async queryIsolatedFiles(): Promise<void> {
    console.log('\n------ Isolated Files ------');
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH (file:File)
WHERE NOT (file)-[:IMPORTS]->() AND NOT ()-[:IMPORTS]->(file)
RETURN file.path
    `);
    
    try {
      const query = `
        MATCH (file:File)
        WHERE NOT (file)-[:IMPORTS]->() AND NOT ()-[:IMPORTS]->(file)
        RETURN file.path AS filePath
      `;
      
      const result = await this.client.runQuery<{ filePath: string }>(query);
      const isolatedFiles = result.map(record => record.filePath);
      
      console.log('Results:');
      if (isolatedFiles.length === 0) {
        console.log('No isolated files found');
      } else {
        isolatedFiles.forEach((file: string, idx: number) => {
          console.log(`${idx + 1}. ${file}`);
        });
        console.log(`Total: ${isolatedFiles.length} isolated files`);
      }
      
      console.log('Interpretation:');
      console.log('These files are not connected to the rest of your codebase:');
      console.log('1. They might be unused and candidates for removal');
      console.log('2. They could be entry points like main.ts files');
      console.log('3. They might represent issues with your import analysis');
    } catch (error) {
      console.error('Error querying isolated files:', error);
    }
  }

  /**
   * Queries file clustering analysis to identify cohesive modules
   */
  async queryFileClustering(): Promise<void> {
    console.log('\n------ Directory Clustering Analysis ------');
    
    console.log('Equivalent Cypher query:');
    console.log(`
MATCH (file:File)
WITH split(file.path, '/') AS parts
WITH parts[size(parts)-2] AS directory, count(*) AS fileCount
WHERE directory IS NOT NULL
RETURN directory, fileCount
ORDER BY fileCount DESC
LIMIT 10
    `);
    
    try {
      // First get directory structure
      const query1 = `
        MATCH (file:File)
        WITH split(file.path, '/') AS parts
        WITH parts[size(parts)-2] AS directory, count(*) AS fileCount
        WHERE directory IS NOT NULL
        RETURN directory, fileCount
        ORDER BY fileCount DESC
        LIMIT 10
      `;
      
      const directoryCounts = await this.client.runQuery<{ directory: string; fileCount: any }>(query1);
      const dirCounts = directoryCounts.map(record => ({
        directory: record.directory,
        count: typeof record.fileCount === 'number' ? record.fileCount : parseInt(record.fileCount.toString())
      }));
      
      console.log('Directory Structure:');
      dirCounts.forEach((dir: { directory: string; count: number }, idx: number) => {
        console.log(`${idx + 1}. ${dir.directory}: ${dir.count} files`);
      });
      
      // Then get inter-directory connections
      console.log('\nDirectory Connections:');
      console.log('Equivalent Cypher query:');
      console.log(`
MATCH (f1:File)-[:IMPORTS]->(f2:File)
WITH split(f1.path, '/') AS parts1, split(f2.path, '/') AS parts2
WITH parts1[size(parts1)-2] AS dir1, parts2[size(parts2)-2] AS dir2
WHERE dir1 <> dir2 AND dir1 IS NOT NULL AND dir2 IS NOT NULL
RETURN dir1, dir2, count(*) AS connections
ORDER BY connections DESC
LIMIT 10
      `);
      
      const query2 = `
        MATCH (f1:File)-[:IMPORTS]->(f2:File)
        WITH split(f1.path, '/') AS parts1, split(f2.path, '/') AS parts2
        WITH parts1[size(parts1)-2] AS dir1, parts2[size(parts2)-2] AS dir2
        WHERE dir1 <> dir2 AND dir1 IS NOT NULL AND dir2 IS NOT NULL
        RETURN dir1, dir2, count(*) AS connections
        ORDER BY connections DESC
        LIMIT 10
      `;
      
      const directoryConnections = await this.client.runQuery<{ dir1: string; dir2: string; connections: any }>(query2);
      const dirConns = directoryConnections.map(record => ({
        source: record.dir1,
        target: record.dir2,
        count: typeof record.connections === 'number' ? record.connections : parseInt(record.connections.toString())
      }));
      
      dirConns.forEach((conn: { source: string; target: string; count: number }, idx: number) => {
        console.log(`${idx + 1}. ${conn.source} → ${conn.target}: ${conn.count} connections`);
      });
      
      console.log('\nInterpretation:');
      console.log('1. Directories with many files might indicate too much responsibility');
      console.log('2. High inter-directory connections suggest tight coupling');
      console.log('3. Consider refactoring directories with many outgoing connections');
    } catch (error) {
      console.error('Error querying file clustering:', error);
    }
  }

  /**
   * Generates a simple text representation of a dependency graph
   * @param filePath - The starting file path
   * @param depth - The maximum depth to traverse
   */
  async queryDependencyGraph(filePath: string, depth: number = 2): Promise<void> {
    console.log(`\n------ Dependency Graph for ${filePath} (depth: ${depth}) ------`);
    
    try {
      const query = `
        MATCH path = (file:File {path: $filePath})-[r:IMPORTS*1..${depth}]->(dependency:File)
        RETURN path
      `;
      
      const result = await this.client.runQuery(query, { filePath });
      
      if (result.length === 0) {
        console.log('No dependencies found');
        return;
      }
      
      // Extract the paths from result records
      const paths: string[][] = [];
      
      result.forEach(record => {
        if (record.path) {
          const path = record.path;
          const segments = path.segments;
          
          const pathNodes: string[] = [];
          for (let i = 0; i < segments.length; i++) {
            const segment = segments[i];
            if (i === 0) {
              pathNodes.push(segment.start.properties.path);
            }
            pathNodes.push(segment.end.properties.path);
          }
          
          paths.push(pathNodes);
        }
      });
      
      // Build a tree structure
      const tree: { [key: string]: string[] } = {};
      
      paths.forEach((path: string[]) => {
        for (let i = 0; i < path.length - 1; i++) {
          const source = path[i];
          const target = path[i + 1];
          
          if (!tree[source]) {
            tree[source] = [];
          }
          
          if (!tree[source].includes(target)) {
            tree[source].push(target);
          }
        }
      });
      
      // Print as text tree
      console.log('Results:');
      
      const visited = new Set<string>();
      const printTree = (node: string, indent: string = '') => {
        console.log(`${indent}${node.split('/').pop()}`);
        
        if (visited.has(node)) {
          console.log(`${indent}  ... (cyclic reference)`);
          return;
        }
        
        visited.add(node);
        
        if (tree[node]) {
          tree[node].forEach((child, idx) => {
            const isLast = idx === tree[node].length - 1;
            const childIndent = indent + (isLast ? '  └─ ' : '  ├─ ');
            const nestedIndent = indent + (isLast ? '     ' : '  │  ');
            
            if (child.split('/').pop() === node.split('/').pop()) {
              console.log(`${childIndent}${child}`);
            } else {
              console.log(`${childIndent}${child.split('/').pop()}`);
            }
            
            if (tree[child] && !visited.has(child)) {
              tree[child].forEach((grandchild, grandIdx) => {
                const isLastGrand = grandIdx === tree[child].length - 1;
                printTree(grandchild, nestedIndent + (isLastGrand ? '  └─ ' : '  ├─ '));
              });
            }
          });
        }
        
        visited.delete(node);
      };
      
      printTree(filePath);
      
      console.log('\nInterpretation:');
      console.log('This tree shows the dependency hierarchy starting from the given file.');
      console.log('Each level represents direct imports and their subsequent imports.');
    } catch (error) {
      console.error('Error generating dependency graph:', error);
    }
  }

  /**
   * Run all queries as a demonstration
   */
  async runAllQueries(): Promise<void> {
    try {
      console.log('============================================================');
      console.log('  GRAPHITI CLIENT QUERY EXAMPLES');
      console.log('============================================================');
      
      const testFile = await this.findSampleFile();
      
      if (!testFile) {
        console.log('No sample file found. Please specify a file manually.');
        return;
      }
      
      console.log(`Using sample file: ${testFile}`);
      
      await this.queryDirectDependencies(testFile);
      await this.queryReverseDependencies(testFile);
      await this.queryMostImportedFiles(5);
      await this.queryDependencyChains(testFile, 2);
      await this.queryIsolatedFiles();
      await this.queryFileClustering();
      await this.queryDependencyGraph(testFile, 2);
      
      console.log('\n============================================================');
      console.log('  QUERY EXAMPLES COMPLETE');
      console.log('============================================================');
    } catch (error) {
      console.error('Error running all queries:', error);
    } finally {
      await this.close();
    }
  }

  /**
   * Find a sample TypeScript file to use for the queries
   */
  private async findSampleFile(): Promise<string | null> {
    try {
      // First try to find a file with both imports and importers
      const query1 = `
        MATCH (file:File)-[:IMPORTS]->()
        WITH file
        MATCH ()-[:IMPORTS]->(file)
        RETURN file.path AS path
        LIMIT 1
      `;
      
      const results = await this.client.runQuery<{ path: string }>(query1);
      
      if (results.length > 0) {
        return results[0].path;
      }
      
      // If not found, try any file with imports
      const query2 = `
        MATCH (file:File)-[:IMPORTS]->()
        RETURN file.path AS path
        LIMIT 1
      `;
      
      const fallbackResults = await this.client.runQuery<{ path: string }>(query2);
      
      if (fallbackResults.length > 0) {
        return fallbackResults[0].path;
      }
      
      // If still nothing, try any file
      const query3 = `
        MATCH (file:File)
        RETURN file.path AS path
        LIMIT 1
      `;
      
      const lastResortResults = await this.client.runQuery<{ path: string }>(query3);
      
      if (lastResortResults.length > 0) {
        return lastResortResults[0].path;
      }
      
      return null;
    } catch (error) {
      console.error('Error finding sample file:', error);
      return null;
    }
  }

  /**
   * Close the Neo4j client connection
   */
  async close(): Promise<void> {
    try {
      await this.client.close();
    } catch (error) {
      console.error('Error closing client:', error);
    }
  }
}

// Run the queries when called directly
if (require.main === module) {
  const tester = new TestGraphitiQueries();
  tester.runAllQueries().catch(err => {
    console.error('Error running queries:', err);
    process.exit(1);
  });
}

export default TestGraphitiQueries; 