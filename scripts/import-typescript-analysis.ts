import { GraphitiClient } from '../packages/core/src/graph/graphiti-client';
import fs from 'fs';
import path from 'path';

async function importData() {
  // Initialize GraphitiClient with Neo4j connection details
  const client = new GraphitiClient({
    uri: process.env.NEO4J_URI || 'bolt://localhost:7687',
    username: process.env.NEO4J_USER || 'neo4j',
    password: process.env.NEO4J_PASSWORD || 'password',
    database: process.env.NEO4J_DATABASE || 'neo4j'
  });
  
  try {
    // Read the analysis data
    const dataPath = process.env.ANALYSIS_FILE || './outputs/typescript/typescript-analysis-typescript-repo-2025-04-27.json';
    console.log(`Reading analysis data from ${dataPath}...`);
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    // Initialize schema if needed
    console.log('Initializing database schema...');
    await client.initSchema();
    
    // Clear existing data
    console.log('Clearing existing database data...');
    await client.clearDatabase();
    
    // Create a map to store entity IDs and their corresponding file paths
    const entityMap = new Map();
    
    // Create file nodes
    console.log(`Importing ${data.entities.length} entities...`);
    for (const entity of data.entities) {
      if (entity.type === 'File') {
        try {
          // Store the mapping between entity ID and file path
          entityMap.set(entity.id, entity.filePath);
          
          await client.createFileNodeFromEntity(entity);
          process.stdout.write('.');
        } catch (error) {
          console.error(`Error creating entity ${entity.id}:`, error);
        }
      }
    }
    console.log('\nEntities import complete.');
    
    // Create relationships
    console.log(`Importing ${data.relationships.length} relationships...`);
    for (const rel of data.relationships) {
      if (rel.type === 'IMPORTS') {
        try {
          // Get the file paths from the entity map
          const sourcePath = entityMap.get(rel.source);
          const targetPath = entityMap.get(rel.target);
          
          if (!sourcePath || !targetPath) {
            console.error(`Skipping relationship: Could not find file paths for ${rel.source} -> ${rel.target}`);
            continue;
          }
          
          await client.createImportRelationship(
            sourcePath,
            targetPath,
            rel.properties.importType
          );
          process.stdout.write('.');
        } catch (error) {
          console.error(`Error creating relationship ${rel.source} -> ${rel.target}:`, error);
        }
      }
    }
    console.log('\nRelationships import complete.');
    
    console.log('Import completed successfully');
  } catch (error) {
    console.error('Import failed:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Run the import process
importData().catch(error => {
  console.error('Unhandled error during import:', error);
  process.exit(1);
}); 