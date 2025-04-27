#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import * as path from 'path';
import * as fs from 'fs/promises';
import { GraphitiClient, FileMetadata, ImportType } from '@codex-arch/core';
import { TypeScriptParser } from '@codex-arch/parsers-typescript';

const program = new Command();

// Initialize CLI configuration
program
  .name('codex-arch')
  .description('Codebase architecture analysis tool that builds a knowledge graph of code relationships')
  .version('0.1.0');

// Config command
program
  .command('config')
  .description('Configure connection to the Neo4j database')
  .option('--uri <uri>', 'Neo4j server URI', 'bolt://localhost:7687')
  .option('--username <username>', 'Neo4j username', 'neo4j')
  .option('--password <password>', 'Neo4j password', 'password')
  .option('--database <database>', 'Neo4j database name', 'neo4j')
  .action(async (options) => {
    try {
      const configDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.codex-arch');
      await fs.mkdir(configDir, { recursive: true });
      
      const configPath = path.join(configDir, 'config.json');
      await fs.writeFile(configPath, JSON.stringify({
        neo4j: {
          uri: options.uri,
          username: options.username,
          password: options.password,
          database: options.database
        }
      }, null, 2));
      
      console.log(chalk.green('✓ Configuration saved successfully'));
    } catch (error) {
      console.error(chalk.red('✗ Failed to save configuration:'), error);
      process.exit(1);
    }
  });

// Analyze command
program
  .command('analyze')
  .description('Analyze a codebase and build a knowledge graph')
  .argument('<dir>', 'Directory to analyze')
  .option('-e, --exclude <patterns...>', 'Glob patterns to exclude')
  .option('-i, --include <patterns...>', 'Glob patterns to include')
  .option('--no-imports', 'Exclude imports analysis')
  .option('--no-inheritance', 'Exclude inheritance analysis')
  .option('--no-calls', 'Exclude function calls analysis')
  .option('-o, --output <file>', 'Save analysis results to file (JSON)')
  .action(async (dir, options) => {
    try {
      console.log(chalk.blue('Analyzing codebase at:'), dir);
      
      // Load configuration
      const configDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.codex-arch');
      const configPath = path.join(configDir, 'config.json');
      
      let config;
      try {
        const configContent = await fs.readFile(configPath, 'utf-8');
        config = JSON.parse(configContent);
      } catch (error) {
        console.error(chalk.yellow('! Configuration not found, using defaults'));
        config = {
          neo4j: {
            uri: 'bolt://localhost:7687',
            username: 'neo4j',
            password: 'password',
            database: 'neo4j'
          }
        };
      }
      
      // Initialize graph client
      const graphClient = new GraphitiClient(config.neo4j);
      console.log(chalk.blue('Connected to Neo4j at:'), config.neo4j.uri);
      
      // Initialize schema
      console.log(chalk.blue('Initializing schema...'));
      await graphClient.initSchema();
      
      // Initialize TypeScript parser
      const parser = new TypeScriptParser();
      
      // Parse the codebase
      console.log(chalk.blue('Parsing TypeScript files...'));
      const parseResult = await parser.parseDirectory(dir, {
        exclude: options.exclude,
        include: options.include,
        recursive: true
      });
      
      console.log(chalk.green(`✓ Analysis complete. Found ${parseResult.entities.length} entities and ${parseResult.relationships.length} relationships.`));
      
      // Save analysis results to file if requested
      if (options.output) {
        await fs.writeFile(options.output, JSON.stringify({
          entities: parseResult.entities,
          relationships: parseResult.relationships,
          summary: {
            entityCount: parseResult.entities.length,
            relationshipCount: parseResult.relationships.length,
            timestamp: new Date().toISOString(),
            repository: path.resolve(dir)
          }
        }, null, 2));
        console.log(chalk.blue(`Analysis results saved to ${options.output}`));
      }
      
      // Store file entities in Neo4j
      console.log(chalk.blue('Storing files in Neo4j...'));
      let filesCreated = 0;
      
      for (const entity of parseResult.entities) {
        if (entity.type === 'File') {
          const metadata: FileMetadata = {
            name: entity.name,
            extension: entity.properties.ext || '',
            size: entity.properties.size || 0
          };
          
          await graphClient.createFileNode(entity.filePath, metadata);
          filesCreated++;
          
          // Show progress
          if (filesCreated % 10 === 0 || filesCreated === parseResult.entities.length) {
            process.stdout.write(`\r${chalk.green('✓')} Created ${filesCreated}/${parseResult.entities.length} file nodes`);
          }
        }
      }
      console.log(); // New line after progress
      
      // Store import relationships
      console.log(chalk.blue('Storing import relationships in Neo4j...'));
      let importsCreated = 0;
      
      if (options.imports) {
        for (const relationship of parseResult.relationships) {
          if (relationship.type === 'IMPORTS') {
            const sourceEntity = parseResult.entities.find(e => e.id === relationship.source);
            const targetEntity = parseResult.entities.find(e => e.id === relationship.target);
            
            if (sourceEntity && targetEntity) {
              await graphClient.createImportRelationship(
                sourceEntity.filePath,
                targetEntity.filePath,
                relationship.properties.importType || ImportType.Named
              );
              importsCreated++;
              
              // Show progress
              if (importsCreated % 10 === 0 || importsCreated === parseResult.relationships.length) {
                process.stdout.write(`\r${chalk.green('✓')} Created ${importsCreated}/${parseResult.relationships.length} import relationships`);
              }
            }
          }
        }
      } else {
        console.log(chalk.yellow('! Import analysis skipped'));
      }
      console.log(); // New line after progress
      
      console.log(chalk.green(`✓ Data stored successfully in the graph database`));
      console.log(chalk.green(`  - ${filesCreated} file nodes created`));
      console.log(chalk.green(`  - ${importsCreated} import relationships created`));
      
      // Cleanup
      await graphClient.close();
      
    } catch (error) {
      console.error(chalk.red('✗ Analysis failed:'), error);
      process.exit(1);
    }
  });

// Query command
program
  .command('query')
  .description('Run a Cypher query against the code knowledge graph')
  .argument('<cypher-query>', 'Cypher query to execute')
  .option('-p, --param <params...>', 'Query parameters as key=value pairs')
  .option('-o, --output <file>', 'Output file for results (JSON)')
  .action(async (query, options) => {
    try {
      // Parse parameters
      const params: Record<string, any> = {};
      if (options.param) {
        for (const param of options.param) {
          const [key, value] = param.split('=');
          if (key && value) {
            params[key] = value;
          }
        }
      }
      
      // Load configuration
      const configDir = path.join(process.env.HOME || process.env.USERPROFILE || '', '.codex-arch');
      const configPath = path.join(configDir, 'config.json');
      
      let config;
      try {
        const configContent = await fs.readFile(configPath, 'utf-8');
        config = JSON.parse(configContent);
      } catch (error) {
        console.error(chalk.yellow('! Configuration not found, using defaults'));
        config = {
          neo4j: {
            uri: 'bolt://localhost:7687',
            username: 'neo4j',
            password: 'password',
            database: 'neo4j'
          }
        };
      }
      
      // Initialize graph client
      const graphClient = new GraphitiClient(config.neo4j);
      
      // Execute query
      console.log(chalk.blue('Executing query...'));
      const results = await graphClient.runQuery(query, params);
      
      // Display results
      console.log(chalk.green(`✓ Query executed successfully. Found ${results.length} results.`));
      
      if (options.output) {
        await fs.writeFile(options.output, JSON.stringify(results, null, 2));
        console.log(chalk.blue(`Results saved to ${options.output}`));
      } else {
        console.log(JSON.stringify(results, null, 2));
      }
      
      // Cleanup
      await graphClient.close();
      
    } catch (error) {
      console.error(chalk.red('✗ Query failed:'), error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse(); 