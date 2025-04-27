import { GraphitiClient } from '@codex-arch/core';

/**
 * MCP Action definitions for codex-arch
 */

/**
 * Base interface for all action parameters
 */
interface ActionParams {
  [key: string]: any;
}

/**
 * Base interface for all action results
 */
interface ActionResult {
  success: boolean;
  error?: string;
  data?: any;
}

/**
 * Interface for MCP action definitions
 */
export interface MCPAction<P extends ActionParams = ActionParams, R extends ActionResult = ActionResult> {
  name: string;
  description: string;
  execute: (params: P) => Promise<R>;
}

/**
 * Parameters for analyzing a code repository
 */
interface AnalyzeRepositoryParams extends ActionParams {
  repositoryPath: string;
  filters?: {
    includePatterns?: string[];
    excludePatterns?: string[];
  };
  options?: {
    includeImports?: boolean;
    includeInheritance?: boolean;
    includeCalls?: boolean;
  };
}

/**
 * Result of repository analysis
 */
interface AnalyzeRepositoryResult extends ActionResult {
  data?: {
    entityCount: number;
    relationshipCount: number;
    fileCount: number;
    graphId: string;
  };
}

/**
 * Parameters for querying the code graph
 */
interface QueryGraphParams extends ActionParams {
  query: string;
  parameters?: Record<string, any>;
}

/**
 * Result of a graph query
 */
interface QueryGraphResult extends ActionResult {
  data?: any[];
}

/**
 * Parameters for finding code paths
 */
interface FindPathParams extends ActionParams {
  sourceEntityId: string;
  targetEntityId: string;
  maxDepth?: number;
  relationshipTypes?: string[];
}

/**
 * Result of finding paths
 */
interface FindPathResult extends ActionResult {
  data?: {
    paths: any[];
    pathCount: number;
  };
}

/**
 * Create MCP actions for codex-arch
 * @param graphClient GraphitiClient instance to use for database operations
 */
export function createMCPActions(graphClient: GraphitiClient): MCPAction<ActionParams, ActionResult>[] {
  // Analyze repository action
  const analyzeRepository: MCPAction<AnalyzeRepositoryParams, AnalyzeRepositoryResult> = {
    name: 'analyze_repository',
    description: 'Analyze a code repository and build a knowledge graph',
    execute: async (params) => {
      try {
        // Placeholder for actual implementation
        return {
          success: true,
          data: {
            entityCount: 100,
            relationshipCount: 250,
            fileCount: 20,
            graphId: 'sample-graph-id'
          }
        };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : String(error)
        };
      }
    }
  };

  // Query graph action
  const queryGraph: MCPAction<QueryGraphParams, QueryGraphResult> = {
    name: 'query_graph',
    description: 'Execute a Cypher query against the code knowledge graph',
    execute: async (params) => {
      try {
        const results = await graphClient.runQuery(params.query, params.parameters || {});
        return {
          success: true,
          data: results
        };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : String(error)
        };
      }
    }
  };

  // Find path action
  const findPath: MCPAction<FindPathParams, FindPathResult> = {
    name: 'find_path',
    description: 'Find paths between two code entities in the graph',
    execute: async (params) => {
      try {
        // Placeholder implementation
        const relationshipTypesClause = params.relationshipTypes?.length
          ? `[:${params.relationshipTypes.join('|')}]`
          : '';
          
        const query = `
          MATCH path = shortestPath((source)-[${relationshipTypesClause}*1..${params.maxDepth || 5}]->(target))
          WHERE source.id = $sourceId AND target.id = $targetId
          RETURN path
        `;
        
        const results = await graphClient.runQuery(query, {
          sourceId: params.sourceEntityId,
          targetId: params.targetEntityId
        });
        
        return {
          success: true,
          data: {
            paths: results,
            pathCount: results.length
          }
        };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : String(error)
        };
      }
    }
  };

  return [
    analyzeRepository,
    queryGraph,
    findPath
  ] as MCPAction<ActionParams, ActionResult>[];
} 