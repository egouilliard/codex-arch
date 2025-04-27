import { GraphitiClient } from '../packages/core/src/graph/graphiti-client';

async function runQueries() {
  // Initialize GraphitiClient with Neo4j connection details
  const client = new GraphitiClient({
    uri: process.env.NEO4J_URI || 'bolt://localhost:7687',
    username: process.env.NEO4J_USER || 'neo4j',
    password: process.env.NEO4J_PASSWORD || 'password',
    database: process.env.NEO4J_DATABASE || 'neo4j'
  });
  
  try {
    console.log('Running database queries...');
    
    // Query all files
    const files = await client.queryFiles();
    console.log(`\nFound ${files.length} files in the database:`);
    files.slice(0, 5).forEach(file => console.log(` - ${file.id} (${file.name})`));
    if (files.length > 5) {
      console.log(` ... and ${files.length - 5} more`);
    }
    
    // Query a specific file's imports
    const appFilePath = 'test-repositories/typescript-repo/src/components/App.tsx';
    console.log(`\nQuerying imports for ${appFilePath}...`);
    const imports = await client.queryRelationships(appFilePath, 'IMPORTS');
    console.log(`${appFilePath} imports ${imports.length} files:`);
    imports.forEach(imp => console.log(` - ${imp.target} (${imp.importType})`));
    
    // Find which files import a specific file
    const helpersFilePath = 'test-repositories/typescript-repo/src/utils/helpers.ts';
    console.log(`\nQuerying which files import ${helpersFilePath}...`);
    const importedBy = await client.queryReverseRelationships(helpersFilePath, 'IMPORTS');
    console.log(`${helpersFilePath} is imported by ${importedBy.length} files:`);
    importedBy.forEach(imp => console.log(` - ${imp.source} (${imp.importType})`));
    
    // Run a custom Cypher query to find most imported file
    console.log('\nFinding most commonly imported files...');
    const mostImportedQuery = `
      MATCH (f:File)<-[r:IMPORTS]-()
      WITH f, count(r) as importCount
      ORDER BY importCount DESC
      LIMIT 5
      RETURN f.path as file, importCount
    `;
    const mostImported = await client.runQuery(mostImportedQuery);
    console.log('Most imported files:');
    mostImported.forEach(record => console.log(` - ${record.file}: imported ${record.importCount} times`));
    
    // Run a custom Cypher query to find files with no imports or importers
    console.log('\nFinding isolated files (no imports or importers)...');
    const isolatedFilesQuery = `
      MATCH (f:File)
      WHERE NOT (f)-[:IMPORTS]->() AND NOT ()-[:IMPORTS]->(f)
      RETURN f.path as file
    `;
    const isolatedFiles = await client.runQuery(isolatedFilesQuery);
    console.log(`Found ${isolatedFiles.length} isolated files:`);
    isolatedFiles.slice(0, 5).forEach(record => console.log(` - ${record.file}`));
    if (isolatedFiles.length > 5) {
      console.log(` ... and ${isolatedFiles.length - 5} more`);
    }
    
    console.log('\nQueries completed successfully');
  } catch (error) {
    console.error('Query execution failed:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Run the queries
runQueries().catch(error => {
  console.error('Unhandled error during queries:', error);
  process.exit(1);
}); 