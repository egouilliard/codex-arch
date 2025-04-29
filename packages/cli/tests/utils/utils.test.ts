/**
 * Tests for CLI utilities
 */

import fs from 'fs';
import path from 'path';
import { 
  CodexConfig, 
  DatabaseConnection, 
  FileDependencyResult, 
  FileStatResult 
} from '../../src/types';

// Import specific functions from utility modules
import {
  loadConfig,
  saveConfig,
  resetConfig,
  ensureOutputDirectories
} from '../../src/utils/config';

import {
  formatAsJSON,
  formatAsTable,
  formatOutput
} from '../../src/utils/formatters';

import {
  generateVisualizationData,
  generateVisualization,
  saveVisualization
} from '../../src/utils/visualization';

describe('Config utilities', () => {
  // Save current config if any
  let originalConfig: CodexConfig | null = null;
  
  beforeAll(() => {
    try {
      originalConfig = loadConfig();
    } catch (error) {
      originalConfig = null;
    }
  });
  
  afterAll(() => {
    if (originalConfig) {
      saveConfig(originalConfig);
    } else {
      resetConfig();
    }
  });
  
  test('loadConfig should return a valid configuration', () => {
    const conf = loadConfig();
    expect(conf).toBeDefined();
    expect(conf.neo4j).toBeDefined();
    expect(conf.output).toBeDefined();
    expect(conf.analysis).toBeDefined();
  });
  
  test('saveConfig should update configuration', () => {
    const customConfig = {
      neo4j: {
        uri: 'bolt://localhost:7688',
        username: 'test',
        password: 'test'
      }
    };
    
    saveConfig(customConfig);
    const conf = loadConfig();
    
    expect(conf.neo4j.uri).toBe('bolt://localhost:7688');
    expect(conf.neo4j.username).toBe('test');
    expect(conf.neo4j.password).toBe('test');
  });
  
  test('ensureOutputDirectories should create directories', () => {
    const testConfig: CodexConfig = {
      neo4j: {
        uri: 'bolt://localhost:7687',
        username: 'neo4j',
        password: 'password'
      },
      output: {
        root: './test-outputs',
        typescript: './test-outputs/typescript',
        visualizations: './test-outputs/visualizations'
      },
      analysis: {
        exclude: ['node_modules']
      }
    };
    
    ensureOutputDirectories(testConfig);
    
    expect(fs.existsSync('./test-outputs')).toBe(true);
    expect(fs.existsSync('./test-outputs/typescript')).toBe(true);
    expect(fs.existsSync('./test-outputs/visualizations')).toBe(true);
    
    // Clean up
    fs.rmSync('./test-outputs', { recursive: true, force: true });
  });
});

describe('Formatters utilities', () => {
  test('formatAsJSON should format objects as JSON', () => {
    const data = { a: 1, b: 'test' };
    const formatted = formatAsJSON(data);
    
    expect(formatted).toBe(JSON.stringify(data, null, 2));
  });
  
  test('formatAsTable should format data as a table', () => {
    const data = [
      { name: 'John', age: 30 },
      { name: 'Jane', age: 25 }
    ];
    
    const formatted = formatAsTable(data, ['name', 'age']);
    
    expect(formatted).toContain('John');
    expect(formatted).toContain('Jane');
    expect(formatted).toContain('30');
    expect(formatted).toContain('25');
  });
  
  test('formatOutput should handle different result types', () => {
    const depResult: FileDependencyResult = {
      executionTime: 100,
      recordCount: 1,
      records: [
        { source: 'file1.ts', target: 'file2.ts', relationship: 'IMPORTS' }
      ]
    };
    
    const statResult: FileStatResult = {
      executionTime: 100,
      recordCount: 1,
      records: [
        { path: 'file1.ts', count: 5 }
      ]
    };
    
    const depFormatted = formatOutput(depResult, 'json');
    const statFormatted = formatOutput(statResult, 'json');
    
    expect(depFormatted).toContain('file1.ts');
    expect(depFormatted).toContain('file2.ts');
    expect(statFormatted).toContain('file1.ts');
    expect(statFormatted).toContain('5');
  });
});

describe('Visualization utilities', () => {
  test('generateVisualizationData should convert dependency data to graph format', () => {
    const depResult: FileDependencyResult = {
      executionTime: 100,
      recordCount: 2,
      records: [
        { source: 'file1.ts', target: 'file2.ts', relationship: 'IMPORTS' },
        { source: 'file1.ts', target: 'file3.ts', relationship: 'IMPORTS' }
      ]
    };
    
    const graphData = generateVisualizationData(depResult, {
      type: 'dependency-graph',
      format: 'html'
    });
    
    expect(graphData.nodes.length).toBe(3);
    expect(graphData.links.length).toBe(2);
    
    // Check nodes
    const nodeIds = graphData.nodes.map(n => n.id);
    expect(nodeIds).toContain('file1.ts');
    expect(nodeIds).toContain('file2.ts');
    expect(nodeIds).toContain('file3.ts');
    
    // Check links
    expect(graphData.links[0].source).toBe('file1.ts');
    expect(graphData.links[0].target).toBe('file2.ts');
    expect(graphData.links[1].source).toBe('file1.ts');
    expect(graphData.links[1].target).toBe('file3.ts');
  });
  
  test('generateVisualization should create HTML content', () => {
    const depResult: FileDependencyResult = {
      executionTime: 100,
      recordCount: 1,
      records: [
        { source: 'file1.ts', target: 'file2.ts', relationship: 'IMPORTS' }
      ]
    };
    
    const html = generateVisualization(depResult, {
      type: 'dependency-graph',
      format: 'html'
    });
    
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('Codex-Arch Visualization');
    expect(html).toContain('file1.ts');
    expect(html).toContain('file2.ts');
  });
  
  test('saveVisualization should write content to a file', () => {
    const content = '<html><body>Test</body></html>';
    const outputPath = './test-visualization.html';
    
    const filePath = saveVisualization(content, outputPath);
    
    expect(fs.existsSync(outputPath)).toBe(true);
    expect(fs.readFileSync(outputPath, 'utf-8')).toBe(content);
    
    // Clean up
    fs.unlinkSync(outputPath);
  });
});

// We can't easily test database functions in a unit test without a Neo4j instance
// so we'll mock the dependencies in a real integration test 