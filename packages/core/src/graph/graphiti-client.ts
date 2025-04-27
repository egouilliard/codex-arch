import neo4j, { Driver, Session, RecordShape } from 'neo4j-driver';

export interface GraphitiClientConfig {
  uri: string;
  username: string;
  password: string;
  database?: string;
}

/**
 * GraphitiClient provides integration with Neo4j graph database
 * for storing and querying the code knowledge graph
 */
export class GraphitiClient {
  private driver: Driver;
  private database: string;

  constructor(config: GraphitiClientConfig) {
    this.driver = neo4j.driver(
      config.uri,
      neo4j.auth.basic(config.username, config.password)
    );
    this.database = config.database || 'neo4j';
  }

  /**
   * Get a new session
   */
  public getSession(): Session {
    return this.driver.session({ database: this.database });
  }

  /**
   * Run a Cypher query
   */
  public async runQuery<T extends RecordShape = RecordShape>(
    query: string,
    params: Record<string, any> = {}
  ): Promise<T[]> {
    const session = this.getSession();
    try {
      const result = await session.run(query, params);
      return result.records.map(record => record.toObject() as T);
    } finally {
      await session.close();
    }
  }

  /**
   * Create a node in the graph
   */
  public async createNode(
    label: string,
    properties: Record<string, any>
  ): Promise<string> {
    const query = `
      CREATE (n:${label} $properties)
      RETURN n.id as id
    `;
    const result = await this.runQuery<{ id: string }>(query, { properties });
    return result[0]?.id;
  }

  /**
   * Create a relationship between nodes
   */
  public async createRelationship(
    sourceId: string,
    targetId: string,
    type: string,
    properties: Record<string, any> = {}
  ): Promise<void> {
    const query = `
      MATCH (source), (target)
      WHERE source.id = $sourceId AND target.id = $targetId
      CREATE (source)-[r:${type} $properties]->(target)
      RETURN r
    `;
    await this.runQuery(query, { sourceId, targetId, properties });
  }

  /**
   * Close the driver when done
   */
  public async close(): Promise<void> {
    await this.driver.close();
  }
} 