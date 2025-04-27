import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = promisify(exec);

/**
 * Run a command and log its output
 */
async function runCommand(command: string, description: string): Promise<void> {
  console.log(`\n=== ${description} ===`);
  try {
    const { stdout, stderr } = await execAsync(command);
    if (stdout) console.log(stdout);
    if (stderr) console.error(stderr);
  } catch (error) {
    console.error(`Error executing ${description}:`, error);
    throw error;
  }
}

/**
 * Check if docker is running
 */
async function isDockerRunning(): Promise<boolean> {
  try {
    await execAsync('docker info');
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Check if neo4j container is running
 */
async function isNeo4jRunning(): Promise<boolean> {
  try {
    const { stdout } = await execAsync('docker ps --filter "name=neo4j" --format "{{.Names}}"');
    return stdout.includes('neo4j');
  } catch (error) {
    return false;
  }
}

/**
 * Main workflow function
 */
async function runWorkflow() {
  try {
    // Define paths
    const testRepoPath = path.join(process.cwd(), 'test-repositories', 'typescript-repo');
    const outputDir = path.join(process.cwd(), 'outputs', 'typescript');
    const analysisOutputPath = path.join(outputDir, 'typescript-analysis-typescript-repo-2025-04-27.json');
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 1. Run TypeScript analysis on the test repository
    console.log('\n=== Starting Graphiti workflow ===');
    console.log('Step 1: Running TypeScript analysis...');
    
    if (!fs.existsSync(testRepoPath)) {
      console.error(`Test repository not found at: ${testRepoPath}`);
      console.error('Please ensure the typescript-repo exists in the test-repositories directory.');
      process.exit(1);
    }
    
    await runCommand(
      `npx lerna run build --scope=@codex-arch/cli --scope=@codex-arch/core --scope=@codex-arch/parsers-typescript`,
      'Building required packages'
    );
    
    await runCommand(
      `node packages/cli/dist/index.js analyze ${testRepoPath} --exclude "node_modules" "dist" --output ${analysisOutputPath}`,
      'Running TypeScript analysis'
    );
    
    // Verify that the analysis output file exists
    if (!fs.existsSync(analysisOutputPath)) {
      console.error(`Analysis output file not found at: ${analysisOutputPath}`);
      console.error('The analysis may have failed or the output file was not created.');
      process.exit(1);
    }
    
    console.log(`Analysis completed successfully. Output saved to: ${analysisOutputPath}`);
    
    // Create docker directory if it doesn't exist
    const dockerDir = path.join(process.cwd(), 'docker');
    if (!fs.existsSync(dockerDir)) {
      fs.mkdirSync(dockerDir, { recursive: true });
      
      // Create docker-compose.yml
      const dockerCompose = `
version: '3'
services:
  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_dbms_memory_heap_max__size=2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs

volumes:
  neo4j_data:
  neo4j_logs:
`;
      fs.writeFileSync(path.join(dockerDir, 'docker-compose.yml'), dockerCompose);
      console.log('Created docker-compose.yml configuration');
    }
    
    // Check if Docker is running
    if (!(await isDockerRunning())) {
      console.error('Docker is not running. Please start Docker and try again.');
      process.exit(1);
    }
    
    // Start Neo4j if not already running
    if (!(await isNeo4jRunning())) {
      console.log('Starting Neo4j container...');
      await runCommand('cd docker && docker-compose up -d', 'Starting Neo4j');
      
      // Wait for Neo4j to be ready
      console.log('Waiting for Neo4j to start (this may take a moment)...');
      let neo4jReady = false;
      let attempts = 0;
      
      while (!neo4jReady && attempts < 30) {
        try {
          const { stdout } = await execAsync('docker logs neo4j 2>&1 | grep "Remote interface available at"');
          if (stdout) {
            neo4jReady = true;
            console.log('Neo4j is ready!');
          }
        } catch (error) {
          // Neo4j not ready yet
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }
      
      if (!neo4jReady) {
        console.warn('Neo4j might not be fully ready yet, but continuing with the workflow...');
      }
    } else {
      console.log('Neo4j is already running.');
    }
    
    // 2. Import the TypeScript analysis data into Neo4j
    console.log('\nStep 2: Importing analysis data into Neo4j...');
    await runCommand(`ANALYSIS_FILE=${analysisOutputPath} npx ts-node scripts/import-typescript-analysis.ts`, 'Importing TypeScript analysis data');
    
    // 3. Run verification queries
    console.log('\nStep 3: Running verification queries...');
    await runCommand('npx ts-node scripts/query-typescript-analysis.ts', 'Running test queries');
    
    // 4. Generate visualization data
    console.log('\nStep 4: Generating visualization data...');
    await runCommand('npx ts-node scripts/visualize-typescript-analysis.ts', 'Generating visualization data');
    
    // 5. Create HTML visualization
    console.log('\nStep 5: Creating HTML visualization...');
    await runCommand('npx ts-node scripts/generate-html-visualization.ts', 'Creating HTML visualization');
    
    // 6. Open the visualization in a browser
    const htmlPath = path.join(process.cwd(), 'outputs', 'visualizations', 'typescript-visualization.html');
    console.log('\nStep 6: Opening visualization in browser...');
    
    try {
      // Try to open the HTML file in the default browser (platform-dependent)
      if (process.platform === 'darwin') {
        // macOS
        await execAsync(`open ${htmlPath}`);
      } else if (process.platform === 'win32') {
        // Windows
        await execAsync(`start ${htmlPath}`);
      } else {
        // Linux/Unix
        await execAsync(`xdg-open ${htmlPath}`);
      }
      console.log('Opened visualization in browser.');
    } catch (error) {
      console.warn('Could not automatically open the visualization in a browser.');
      console.warn('Please open the following file manually:');
    }
    
    // Print final instructions
    console.log('\n=== Workflow completed successfully ===');
    console.log('Neo4j Browser: http://localhost:7474/browser/');
    console.log('Neo4j credentials: neo4j/password');
    console.log(`\nVisualization: ${htmlPath}`);
  } catch (error) {
    console.error('Workflow failed:', error);
    process.exit(1);
  }
}

// Run the workflow
runWorkflow().catch(console.error); 