import neo4j, { Driver, Session, RecordShape } from 'neo4j-driver';

/**
 * Metadata for a file node
 */
export interface FileMetadata {
  name: string;
  extension: string;
  size?: number;
  content?: string;
}

/**
 * Types of imports
 */
export enum ImportType {
  Default = 'DEFAULT',
  Named = 'NAMED',
  Namespace = 'NAMESPACE',
  SideEffect = 'SIDE_EFFECT'
}

/**
 * Result of a dependency query
 */
export interface DependencyResult {
  filePath: string;
  importType: ImportType;
}

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
   * Initialize schema constraints
   */
  public async initSchema(): Promise<void> {
    // Create index on File.path for efficient lookups
    const createFilePathIndex = `
      CREATE CONSTRAINT file_path_unique IF NOT EXISTS
      FOR (f:File) REQUIRE f.path IS UNIQUE
    `;
    await this.runQuery(createFilePathIndex);
  }

  /**
   * Create a file node in the graph
   */
  public async createFileNode(
    filePath: string,
    metadata: FileMetadata
  ): Promise<string> {
    const query = `
      MERGE (f:File {path: $filePath})
      ON CREATE SET 
        f.name = $metadata.name,
        f.extension = $metadata.extension,
        f.size = $metadata.size,
        f.createdAt = timestamp()
      ON MATCH SET 
        f.name = $metadata.name,
        f.extension = $metadata.extension,
        f.size = $metadata.size,
        f.updatedAt = timestamp()
      RETURN f.path as id
    `;
    const result = await this.runQuery<{ id: string }>(query, { 
      filePath, 
      metadata 
    });
    return result[0]?.id;
  }

  /**
   * Create an import relationship between two files
   */
  public async createImportRelationship(
    sourceFilePath: string,
    targetFilePath: string,
    importType: ImportType
  ): Promise<void> {
    const query = `
      MATCH (source:File {path: $sourceFilePath})
      MATCH (target:File {path: $targetFilePath})
      MERGE (source)-[r:IMPORTS {type: $importType}]->(target)
      ON CREATE SET r.createdAt = timestamp()
      ON MATCH SET r.updatedAt = timestamp()
      RETURN r
    `;
    await this.runQuery(query, { 
      sourceFilePath, 
      targetFilePath, 
      importType 
    });
  }

  /**
   * Get files that the specified file depends on
   */
  public async getFileDependencies(
    filePath: string
  ): Promise<DependencyResult[]> {
    const query = `
      MATCH (f:File {path: $filePath})-[r:IMPORTS]->(dep:File)
      RETURN dep.path as filePath, r.type as importType
    `;
    return this.runQuery<DependencyResult>(query, { filePath });
  }

  /**
   * Get files that import the specified file
   */
  public async getFileImporters(
    filePath: string
  ): Promise<DependencyResult[]> {
    const query = `
      MATCH (imp:File)-[r:IMPORTS]->(f:File {path: $filePath})
      RETURN imp.path as filePath, r.type as importType
    `;
    return this.runQuery<DependencyResult>(query, { filePath });
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

  /**
   * Clear the database (for fresh imports)
   */
  public async clearDatabase(): Promise<void> {
    const query = `
      MATCH (n)
      DETACH DELETE n
    `;
    await this.runQuery(query);
  }

  /**
   * Create a file node directly from a CodeEntity object
   */
  public async createFileNodeFromEntity(entity: any): Promise<string> {
    const metadata: FileMetadata = {
      name: entity.name,
      extension: entity.properties.ext || '',
      size: entity.properties.size || 0
    };
    
    return this.createFileNode(entity.filePath, metadata);
  }

  /**
   * Create an import relationship directly from a CodeRelationship object
   */
  public async createImportRelationshipFromRelationship(relationship: any): Promise<void> {
    const importType = relationship.properties.importType as ImportType;
    await this.createImportRelationship(
      relationship.source,
      relationship.target,
      importType
    );
  }

  /**
   * Query all files in the database
   */
  public async queryFiles(): Promise<any[]> {
    const query = `
      MATCH (f:File)
      RETURN f.path as id, f.name as name, f.extension as extension, f.path as filePath
    `;
    return this.runQuery(query);
  }

  /**
   * Query all relationships of a specific type
   */
  public async queryAllRelationships(type: string): Promise<any[]> {
    const query = `
      MATCH (source)-[r:${type}]->(target)
      RETURN source.path as source, target.path as target, type(r) as type, r.type as importType
    `;
    return this.runQuery(query);
  }

  /**
   * Query relationships from a source node
   */
  public async queryRelationships(sourceId: string, type: string): Promise<any[]> {
    const query = `
      MATCH (source:File {path: $sourceId})-[r:${type}]->(target)
      RETURN source.path as source, target.path as target, type(r) as type, r.type as importType
    `;
    return this.runQuery(query, { sourceId });
  }

  /**
   * Query relationships to a target node
   */
  public async queryReverseRelationships(targetId: string, type: string): Promise<any[]> {
    const query = `
      MATCH (source)-[r:${type}]->(target:File {path: $targetId})
      RETURN source.path as source, target.path as target, type(r) as type, r.type as importType
    `;
    return this.runQuery(query, { targetId });
  }

  /**
   * Generate visualization data with D3.js compatible format
   */
  public async generateVisualizationData(): Promise<{
    nodes: any[],
    links: any[]
  }> {
    const files = await this.queryFiles();
    const relationships = await this.queryAllRelationships('IMPORTS');
    
    return {
      nodes: files.map(file => ({
        id: file.id,
        name: file.name,
        group: file.filePath.split('/').slice(-2)[0] // Group by folder
      })),
      links: relationships.map(rel => ({
        source: rel.source,
        target: rel.target,
        value: 1,
        type: rel.importType
      }))
    };
  }
} 