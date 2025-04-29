/**
 * Database connection utilities for Neo4j in the Codex-Arch CLI
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import neo4j, { Driver, Session, QueryResult } from 'neo4j-driver';
import { CodexConfig, DatabaseConnection } from '../types';

const execAsync = promisify(exec);

// Default Neo4j port
const DEFAULT_NEO4J_PORT = 7687;

// Default Docker image
const DOCKER_IMAGE = 'neo4j:4.4';

/**
 * Connect to a Neo4j database
 * 
 * @param config - Neo4j connection configuration
 * @returns A Promise resolving to a DatabaseConnection object
 */
export async function connectToNeo4j(config: CodexConfig): Promise<DatabaseConnection> {
  const { neo4j: neo4jConfig } = config;
  
  try {
    // Check if using Docker and start container if needed
    if (neo4jConfig.useDocker) {
      await ensureDockerContainer(neo4jConfig.dockerContainerName || 'codex-arch-neo4j');
    }
    
    // Create Neo4j driver
    const driver = neo4j.driver(
      neo4jConfig.uri,
      neo4j.auth.basic(neo4jConfig.username, neo4jConfig.password)
    );
    
    // Verify connection
    await validateConnection(driver);
    
    return {
      driver,
      uri: neo4jConfig.uri,
      database: neo4jConfig.database,
      isDockerContainer: !!neo4jConfig.useDocker,
      dockerContainerName: neo4jConfig.dockerContainerName,
    };
  } catch (error) {
    throw new Error(`Failed to connect to Neo4j: ${(error as Error).message}`);
  }
}

/**
 * Validate Neo4j connection by executing a simple query
 * 
 * @param driver - Neo4j driver instance
 * @returns A Promise that resolves if the connection is valid
 */
export async function validateConnection(driver: Driver): Promise<void> {
  let session: Session | null = null;
  
  try {
    session = driver.session();
    await session.run('RETURN 1 as n');
  } catch (error) {
    throw new Error(`Neo4j connection validation failed: ${(error as Error).message}`);
  } finally {
    if (session) {
      await session.close();
    }
  }
}

/**
 * Close Neo4j connection
 * 
 * @param connection - DatabaseConnection to close
 * @returns A Promise that resolves when the connection is closed
 */
export async function closeConnection(connection: DatabaseConnection): Promise<void> {
  try {
    await connection.driver.close();
  } catch (error) {
    console.error(`Error closing Neo4j connection: ${(error as Error).message}`);
  }
}

/**
 * Check if a Docker container exists and is running
 * 
 * @param containerName - Docker container name
 * @returns A Promise resolving to a boolean indicating if the container is running
 */
export async function isDockerContainerRunning(containerName: string): Promise<boolean> {
  try {
    const { stdout } = await execAsync(
      `docker ps --filter "name=${containerName}" --format "{{.Names}}"`
    );
    return stdout.trim() === containerName;
  } catch (error) {
    return false;
  }
}

/**
 * Check if a Docker container exists
 * 
 * @param containerName - Docker container name
 * @returns A Promise resolving to a boolean indicating if the container exists
 */
export async function doesDockerContainerExist(containerName: string): Promise<boolean> {
  try {
    const { stdout } = await execAsync(
      `docker ps -a --filter "name=${containerName}" --format "{{.Names}}"`
    );
    return stdout.trim() === containerName;
  } catch (error) {
    return false;
  }
}

/**
 * Start a Docker container
 * 
 * @param containerName - Docker container name
 * @returns A Promise that resolves when the container is started
 */
export async function startDockerContainer(containerName: string): Promise<void> {
  try {
    await execAsync(`docker start ${containerName}`);
    
    // Wait for container to be fully started
    let attempts = 0;
    const maxAttempts = 10;
    
    while (attempts < maxAttempts) {
      try {
        await execAsync(`docker exec ${containerName} cypher-shell -u neo4j -p password "RETURN 1;"`);
        return; // Container is ready
      } catch (error) {
        attempts++;
        if (attempts >= maxAttempts) {
          throw new Error('Timed out waiting for Neo4j container to start');
        }
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
      }
    }
  } catch (error) {
    throw new Error(`Failed to start Docker container: ${(error as Error).message}`);
  }
}

/**
 * Create a new Neo4j Docker container
 * 
 * @param containerName - Docker container name
 * @returns A Promise that resolves when the container is created
 */
export async function createDockerContainer(containerName: string): Promise<void> {
  try {
    await execAsync(
      `docker run -d --name ${containerName} -p ${DEFAULT_NEO4J_PORT}:${DEFAULT_NEO4J_PORT} -p 7474:7474 ` +
      `-e NEO4J_AUTH=neo4j/password ${DOCKER_IMAGE}`
    );
    
    // Wait for container to be fully started
    let attempts = 0;
    const maxAttempts = 20;
    
    while (attempts < maxAttempts) {
      try {
        await execAsync(`docker exec ${containerName} cypher-shell -u neo4j -p password "RETURN 1;"`);
        return; // Container is ready
      } catch (error) {
        attempts++;
        if (attempts >= maxAttempts) {
          throw new Error('Timed out waiting for Neo4j container to start');
        }
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
      }
    }
  } catch (error) {
    throw new Error(`Failed to create Docker container: ${(error as Error).message}`);
  }
}

/**
 * Ensure a Neo4j Docker container exists and is running
 * 
 * @param containerName - Docker container name
 * @returns A Promise that resolves when the container is running
 */
export async function ensureDockerContainer(containerName: string): Promise<void> {
  try {
    // Check if Docker is available
    await execAsync('docker --version');
    
    // Check if container exists
    const containerExists = await doesDockerContainerExist(containerName);
    
    if (containerExists) {
      // Check if container is running
      const containerRunning = await isDockerContainerRunning(containerName);
      
      if (!containerRunning) {
        // Start existing container
        await startDockerContainer(containerName);
      }
    } else {
      // Create and start new container
      await createDockerContainer(containerName);
    }
  } catch (error) {
    if ((error as Error).message.includes('docker: command not found')) {
      throw new Error('Docker is not installed or not available in PATH');
    }
    throw new Error(`Failed to ensure Docker container: ${(error as Error).message}`);
  }
}

/**
 * Stop a Neo4j Docker container
 * 
 * @param containerName - Docker container name
 * @returns A Promise that resolves when the container is stopped
 */
export async function stopDockerContainer(containerName: string): Promise<void> {
  try {
    const containerRunning = await isDockerContainerRunning(containerName);
    
    if (containerRunning) {
      await execAsync(`docker stop ${containerName}`);
    }
  } catch (error) {
    throw new Error(`Failed to stop Docker container: ${(error as Error).message}`);
  }
}

/**
 * Remove a Neo4j Docker container
 * 
 * @param containerName - Docker container name
 * @param force - Whether to force removal
 * @returns A Promise that resolves when the container is removed
 */
export async function removeDockerContainer(
  containerName: string,
  force: boolean = false
): Promise<void> {
  try {
    // Stop container if running
    const containerRunning = await isDockerContainerRunning(containerName);
    if (containerRunning) {
      await stopDockerContainer(containerName);
    }
    
    // Remove container
    const forceFlag = force ? ' -f' : '';
    await execAsync(`docker rm${forceFlag} ${containerName}`);
  } catch (error) {
    throw new Error(`Failed to remove Docker container: ${(error as Error).message}`);
  }
}

/**
 * Execute a Cypher query
 * 
 * @param connection - DatabaseConnection to use
 * @param query - Cypher query to execute
 * @param params - Query parameters
 * @returns A Promise resolving to the query result
 */
export async function executeCypherQuery(
  connection: DatabaseConnection,
  query: string,
  params: Record<string, any> = {}
): Promise<QueryResult> {
  let session: Session | null = null;
  
  try {
    session = connection.database
      ? connection.driver.session({ database: connection.database })
      : connection.driver.session();
      
    return await session.run(query, params);
  } catch (error) {
    throw new Error(`Failed to execute Cypher query: ${(error as Error).message}`);
  } finally {
    if (session) {
      await session.close();
    }
  }
}

export default {
  connectToNeo4j,
  validateConnection,
  closeConnection,
  isDockerContainerRunning,
  doesDockerContainerExist,
  startDockerContainer,
  createDockerContainer,
  ensureDockerContainer,
  stopDockerContainer,
  removeDockerContainer,
  executeCypherQuery,
}; 