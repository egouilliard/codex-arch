import { GraphitiClient } from '../packages/core/src/graph/graphiti-client';
import fs from 'fs';
import path from 'path';

async function generateVisualization() {
  // Initialize GraphitiClient with Neo4j connection details
  const client = new GraphitiClient({
    uri: process.env.NEO4J_URI || 'bolt://localhost:7687',
    username: process.env.NEO4J_USER || 'neo4j',
    password: process.env.NEO4J_PASSWORD || 'password',
    database: process.env.NEO4J_DATABASE || 'neo4j'
  });
  
  try {
    console.log('Generating visualization data...');
    
    // Get all files and their relationships for visualization
    const graphData = await client.generateVisualizationData();
    
    console.log(`Generated visualization data for ${graphData.nodes.length} nodes and ${graphData.links.length} links`);
    
    // Create output directory if it doesn't exist
    const outputDir = path.join(process.cwd(), 'outputs', 'visualizations');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Output to JSON file
    const outputFile = path.join(outputDir, 'typescript-visualization-data.json');
    fs.writeFileSync(outputFile, JSON.stringify(graphData, null, 2));
    console.log(`Visualization data saved to ${outputFile}`);
    
    console.log('Visualization data generation completed successfully');
  } catch (error) {
    console.error('Visualization generation failed:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Run the visualization generation
generateVisualization().catch(error => {
  console.error('Unhandled error during visualization generation:', error);
  process.exit(1);
}); 