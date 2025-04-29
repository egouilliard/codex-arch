/**
 * Configuration utilities for the Codex-Arch CLI
 */

import fs from 'fs';
import path from 'path';
import { CodexConfig } from '../types';

// Import conf using require with type casting
// eslint-disable-next-line @typescript-eslint/no-var-requires
const Conf = require('conf');

// Default configuration values
const defaultConfig: CodexConfig = {
  neo4j: {
    uri: 'bolt://localhost:7687',
    username: 'neo4j',
    password: 'password',
    useDocker: true,
    dockerContainerName: 'codex-arch-neo4j',
  },
  output: {
    root: './outputs',
    typescript: './outputs/typescript',
    visualizations: './outputs/visualizations',
  },
  analysis: {
    exclude: ['**/node_modules/**', '**/dist/**', '**/.git/**'],
    maxDepth: 4,
  },
};

// Create configuration store
const configStore = new Conf({
  projectName: 'codex-arch',
  schema: {
    neo4j: {
      type: 'object',
      properties: {
        uri: { type: 'string' },
        username: { type: 'string' },
        password: { type: 'string' },
        database: { type: 'string', nullable: true },
        useDocker: { type: 'boolean', nullable: true },
        dockerContainerName: { type: 'string', nullable: true },
      },
      required: ['uri', 'username', 'password'],
    },
    output: {
      type: 'object',
      properties: {
        root: { type: 'string' },
        typescript: { type: 'string' },
        visualizations: { type: 'string' },
      },
      required: ['root', 'typescript', 'visualizations'],
    },
    analysis: {
      type: 'object',
      properties: {
        exclude: { 
          type: 'array',
          items: { type: 'string' },
        },
        include: { 
          type: 'array',
          items: { type: 'string' },
          nullable: true,
        },
        maxDepth: { type: 'number', nullable: true },
      },
      required: ['exclude'],
    },
  },
});

/**
 * Initialize configuration with default values if not already set
 */
export function initConfig(): void {
  if (!configStore.has('neo4j') || !configStore.has('output') || !configStore.has('analysis')) {
    configStore.set(defaultConfig);
  }
}

/**
 * Load configuration from the configuration store
 * 
 * @param overrides - Optional configuration overrides
 * @returns The merged configuration
 */
export function loadConfig(overrides?: Partial<CodexConfig>): CodexConfig {
  // Initialize config if it doesn't exist
  initConfig();
  
  // Get stored config
  const storedConfig = configStore.store;
  
  // Merge with overrides if provided
  if (overrides) {
    return mergeConfigs(storedConfig, overrides);
  }
  
  return storedConfig;
}

/**
 * Save configuration to the configuration store
 * 
 * @param config - Configuration to save
 */
export function saveConfig(config: Partial<CodexConfig>): void {
  // Merge with existing config
  const currentConfig = configStore.store;
  const mergedConfig = mergeConfigs(currentConfig, config);
  
  // Update store
  configStore.set(mergedConfig);
}

/**
 * Reset configuration to default values
 */
export function resetConfig(): void {
  configStore.set(defaultConfig);
}

/**
 * Clear all configuration
 */
export function clearConfig(): void {
  configStore.clear();
}

/**
 * Merge two configuration objects
 * 
 * @param base - Base configuration
 * @param override - Override configuration
 * @returns Merged configuration
 */
function mergeConfigs(base: CodexConfig, override: Partial<CodexConfig>): CodexConfig {
  const result = { ...base };
  
  // Merge neo4j config
  if (override.neo4j) {
    result.neo4j = { ...result.neo4j, ...override.neo4j };
  }
  
  // Merge output config
  if (override.output) {
    result.output = { ...result.output, ...override.output };
  }
  
  // Merge analysis config
  if (override.analysis) {
    result.analysis = { ...result.analysis, ...override.analysis };
    
    // Special handling for arrays
    if (override.analysis.exclude) {
      result.analysis.exclude = [...override.analysis.exclude];
    }
    if (override.analysis.include) {
      result.analysis.include = [...override.analysis.include];
    }
  }
  
  return result;
}

/**
 * Ensure output directories exist
 * 
 * @param config - Configuration containing output paths
 */
export function ensureOutputDirectories(config: CodexConfig): void {
  const { output } = config;
  
  // Create output directories if they don't exist
  [output.root, output.typescript, output.visualizations].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Get absolute path for an output file
 * 
 * @param config - Configuration containing output paths
 * @param type - Type of output ('typescript' or 'visualizations')
 * @param filename - Output filename
 * @returns Absolute path to the output file
 */
export function getOutputPath(
  config: CodexConfig,
  type: 'typescript' | 'visualizations',
  filename: string
): string {
  const outputDir = config.output[type];
  return path.resolve(outputDir, filename);
}

/**
 * Apply command-line options to configuration
 * 
 * @param config - Base configuration
 * @param options - Command-line options
 * @returns Updated configuration
 */
export function applyCommandOptions(
  config: CodexConfig,
  options: Record<string, any>
): CodexConfig {
  const result = { ...config };
  
  // Apply Neo4j options
  if (options.neo4jUri) {
    result.neo4j.uri = options.neo4jUri;
  }
  if (options.neo4jUser) {
    result.neo4j.username = options.neo4jUser;
  }
  if (options.neo4jPassword) {
    result.neo4j.password = options.neo4jPassword;
  }
  if (options.neo4jDatabase) {
    result.neo4j.database = options.neo4jDatabase;
  }
  if (options.useDocker !== undefined) {
    result.neo4j.useDocker = options.useDocker;
  }
  
  // Apply output options
  if (options.outputDir) {
    result.output.root = options.outputDir;
    result.output.typescript = path.join(options.outputDir, 'typescript');
    result.output.visualizations = path.join(options.outputDir, 'visualizations');
  }
  
  // Apply analysis options
  if (options.exclude) {
    result.analysis.exclude = Array.isArray(options.exclude)
      ? options.exclude
      : [options.exclude];
  }
  if (options.include) {
    result.analysis.include = Array.isArray(options.include)
      ? options.include
      : [options.include];
  }
  if (options.maxDepth) {
    result.analysis.maxDepth = options.maxDepth;
  }
  
  return result;
}

export default {
  loadConfig,
  saveConfig,
  resetConfig,
  clearConfig,
  ensureOutputDirectories,
  getOutputPath,
  applyCommandOptions,
}; 