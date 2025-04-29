/**
 * Type definitions for the Codex-Arch CLI
 */

import { Driver } from 'neo4j-driver';

/**
 * Configuration for the Codex-Arch CLI
 */
export interface CodexConfig {
  /** Neo4j connection details */
  neo4j: {
    /** Neo4j database URI */
    uri: string;
    /** Neo4j username */
    username: string;
    /** Neo4j password */
    password: string;
    /** Neo4j database name */
    database?: string;
    /** Use Docker container for Neo4j */
    useDocker?: boolean;
    /** Docker container name */
    dockerContainerName?: string;
  };
  /** Output directory paths */
  output: {
    /** Root output directory */
    root: string;
    /** TypeScript analysis output directory */
    typescript: string;
    /** Visualizations output directory */
    visualizations: string;
  };
  /** Analysis configuration */
  analysis: {
    /** Patterns to exclude from analysis */
    exclude: string[];
    /** Patterns to include in analysis */
    include?: string[];
    /** Maximum depth for dependency analysis */
    maxDepth?: number;
  };
}

/**
 * Base interface for query results
 */
export interface BaseQueryResult {
  /** Query execution time in milliseconds */
  executionTime: number;
  /** Total records returned */
  recordCount: number;
}

/**
 * Results from file dependency queries
 */
export interface FileDependencyResult extends BaseQueryResult {
  /** File dependency records */
  records: Array<{
    /** Source file path */
    source: string;
    /** Target file path */
    target: string;
    /** Relationship type */
    relationship: string;
    /** Depth in the dependency tree */
    depth?: number;
  }>;
}

/**
 * Results from file statistical queries
 */
export interface FileStatResult extends BaseQueryResult {
  /** File statistics records */
  records: Array<{
    /** File path */
    path: string;
    /** Count (e.g., import count) */
    count: number;
    /** Additional properties */
    [key: string]: any;
  }>;
}

/**
 * Results from path queries (e.g., connection paths)
 */
export interface PathQueryResult extends BaseQueryResult {
  /** Path records */
  records: Array<{
    /** Array of files in the path */
    path: string[];
    /** Path length */
    length: number;
  }>;
}

/**
 * Results from custom Cypher queries
 */
export interface CustomQueryResult extends BaseQueryResult {
  /** Raw records from Neo4j */
  records: Array<Record<string, any>>;
  /** Keys available in the records */
  keys: string[];
}

/**
 * Union type for all query result types
 */
export type QueryResult = 
  | FileDependencyResult
  | FileStatResult
  | PathQueryResult
  | CustomQueryResult;

/**
 * Configuration for visualization generation
 */
export interface VisualizationOptions {
  /** Type of visualization to generate */
  type: 'dependency-graph' | 'cluster-graph' | 'import-graph';
  /** Output format */
  format: 'html' | 'json' | 'd3';
  /** Output file path */
  outputPath?: string;
  /** Open in browser after generation */
  openInBrowser?: boolean;
  /** Root directory for file paths in visualization */
  rootDir?: string;
  /** Additional visualization options */
  options?: {
    /** Maximum number of nodes to include */
    maxNodes?: number;
    /** Maximum depth of relationships to include */
    maxDepth?: number;
    /** Node grouping strategy */
    groupBy?: 'directory' | 'none';
    /** Custom node colors by pattern */
    nodeColors?: Record<string, string>;
    /** Additional layout options */
    layout?: Record<string, any>;
  };
}

/**
 * Database connection details object
 */
export interface DatabaseConnection {
  /** Neo4j driver instance */
  driver: Driver;
  /** Connected database URI */
  uri: string;
  /** Connected database name */
  database?: string;
  /** Whether connection is using a Docker container */
  isDockerContainer: boolean;
  /** Docker container name if applicable */
  dockerContainerName?: string;
}

/**
 * Format options for CLI output
 */
export type OutputFormat = 'table' | 'json' | 'tree' | 'plain';

/**
 * CLI command status types for progress reporting
 */
export type CommandStatus = 'success' | 'error' | 'warning' | 'info'; 