/**
 * Tests for the config.ts utility functions
 */

import {
  initConfig,
  loadConfig,
  saveConfig,
  resetConfig,
  clearConfig,
  ensureOutputDirectories,
  getOutputPath
} from '../../src/utils/config';
import fs from 'fs';
import path from 'path';
import { CodexConfig } from '../../src/types';

// Mock the fs module
jest.mock('fs', () => ({
  existsSync: jest.fn(),
  mkdirSync: jest.fn(),
}));

describe('config utility', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  describe('loadConfig', () => {
    it('should return configuration with defaults', () => {
      const config = loadConfig();
      
      // Check for expected structure
      expect(config).toHaveProperty('neo4j');
      expect(config).toHaveProperty('output');
      expect(config).toHaveProperty('analysis');
      
      // Check for required properties
      expect(config.neo4j).toHaveProperty('uri');
      expect(config.neo4j).toHaveProperty('username');
      expect(config.neo4j).toHaveProperty('password');
    });

    it('should merge overrides with stored config', () => {
      const overrides: Partial<CodexConfig> = {
        neo4j: {
          uri: 'bolt://custom-host:7687',
          username: 'neo4j',
          password: 'password',
        },
      };
      
      const config = loadConfig(overrides);
      
      expect(config.neo4j.uri).toBe('bolt://custom-host:7687');
    });
  });

  describe('ensureOutputDirectories', () => {
    it('should create output directories if they do not exist', () => {
      // Mock fs.existsSync to return false (directories don't exist)
      (fs.existsSync as jest.Mock).mockReturnValue(false);
      
      const config = {
        neo4j: {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password',
        },
        output: {
          root: './outputs',
          typescript: './outputs/typescript',
          visualizations: './outputs/visualizations',
        },
        analysis: {
          exclude: ['**/node_modules/**'],
        },
      };
      
      ensureOutputDirectories(config);
      
      // Check that mkdirSync was called for each directory
      expect(fs.mkdirSync).toHaveBeenCalledTimes(3);
      expect(fs.mkdirSync).toHaveBeenCalledWith('./outputs', { recursive: true });
      expect(fs.mkdirSync).toHaveBeenCalledWith('./outputs/typescript', { recursive: true });
      expect(fs.mkdirSync).toHaveBeenCalledWith('./outputs/visualizations', { recursive: true });
    });

    it('should not create directories that already exist', () => {
      // Mock fs.existsSync to return true (directories exist)
      (fs.existsSync as jest.Mock).mockReturnValue(true);
      
      const config = {
        neo4j: {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password',
        },
        output: {
          root: './outputs',
          typescript: './outputs/typescript',
          visualizations: './outputs/visualizations',
        },
        analysis: {
          exclude: ['**/node_modules/**'],
        },
      };
      
      ensureOutputDirectories(config);
      
      // Check that mkdirSync was not called
      expect(fs.mkdirSync).not.toHaveBeenCalled();
    });
  });

  describe('getOutputPath', () => {
    it('should return the correct output path for typescript files', () => {
      const config = {
        neo4j: {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password',
        },
        output: {
          root: './outputs',
          typescript: './outputs/typescript',
          visualizations: './outputs/visualizations',
        },
        analysis: {
          exclude: ['**/node_modules/**'],
        },
      };
      
      const result = getOutputPath(config, 'typescript', 'analysis.json');
      
      // Since path.join is not mocked, we need to use actual path joining
      expect(result).toContain('outputs/typescript/analysis.json');
    });

    it('should return the correct output path for visualization files', () => {
      const config = {
        neo4j: {
          uri: 'bolt://localhost:7687',
          username: 'neo4j',
          password: 'password',
        },
        output: {
          root: './outputs',
          typescript: './outputs/typescript',
          visualizations: './outputs/visualizations',
        },
        analysis: {
          exclude: ['**/node_modules/**'],
        },
      };
      
      const result = getOutputPath(config, 'visualizations', 'graph.html');
      
      expect(result).toContain('outputs/visualizations/graph.html');
    });
  });
}); 