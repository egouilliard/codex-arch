/**
 * Output formatting utilities for the Codex-Arch CLI
 */

import chalk from 'chalk';
import { table as createTable } from 'table';
import { QueryResult, OutputFormat, CommandStatus, FileDependencyResult, FileStatResult, PathQueryResult, CustomQueryResult } from '../types';

/**
 * Format output as a table
 * 
 * @param data - Data to format
 * @param headers - Table headers
 * @returns Formatted table string
 */
export function formatAsTable(data: Array<Record<string, any>>, headers: string[]): string {
  // Prepare table data with headers
  const tableData = [
    headers.map(header => chalk.bold(header)),
    ...data.map(row => headers.map(header => formatValue(row[header])))
  ];
  
  // Generate table with default styling
  return createTable(tableData, {
    border: {
      topBody: '─',
      topJoin: '┬',
      topLeft: '┌',
      topRight: '┐',
      bottomBody: '─',
      bottomJoin: '┴',
      bottomLeft: '└',
      bottomRight: '┘',
      bodyLeft: '│',
      bodyRight: '│',
      bodyJoin: '│',
      joinBody: '─',
      joinLeft: '├',
      joinRight: '┤',
      joinJoin: '┼'
    }
  });
}

/**
 * Format output as JSON
 * 
 * @param data - Data to format
 * @param pretty - Whether to pretty-print the JSON
 * @returns Formatted JSON string
 */
export function formatAsJSON(data: any, pretty: boolean = true): string {
  return pretty
    ? JSON.stringify(data, null, 2)
    : JSON.stringify(data);
}

/**
 * Format output as a tree
 * 
 * @param data - Data to format
 * @param options - Tree formatting options
 * @returns Formatted tree string
 */
export function formatAsTree(
  data: FileDependencyResult,
  options: {
    rootNode?: string;
    maxDepth?: number;
    indentSize?: number;
    showRelationship?: boolean;
  } = {}
): string {
  const {
    rootNode,
    maxDepth = Infinity,
    indentSize = 2,
    showRelationship = true
  } = options;
  
  // Get the root node of the tree
  const root = rootNode || findRootNode(data);
  if (!root) {
    return 'No data to display in tree format';
  }
  
  // Build a map of parent to children
  const childrenMap = new Map<string, Array<{ target: string; relationship: string }>>();
  for (const record of data.records) {
    const { source, target, relationship } = record;
    if (!childrenMap.has(source)) {
      childrenMap.set(source, []);
    }
    childrenMap.get(source)!.push({ target, relationship });
  }
  
  // Build the tree recursively
  return buildTreeString(root, childrenMap, 0, maxDepth, indentSize, showRelationship);
}

/**
 * Find the root node in a dependency result
 * 
 * @param data - Dependency result data
 * @returns Root node path
 */
function findRootNode(data: FileDependencyResult): string | undefined {
  const sources = new Set(data.records.map(record => record.source));
  const targets = new Set(data.records.map(record => record.target));
  
  // Find nodes that are sources but not targets (root nodes)
  const rootNodes = Array.from(sources).filter(source => !targets.has(source));
  
  // Return the first root node or undefined if none
  return rootNodes.length > 0 ? rootNodes[0] : undefined;
}

/**
 * Build a string representation of a dependency tree
 * 
 * @param node - Current node
 * @param childrenMap - Map of parent nodes to children
 * @param depth - Current depth in the tree
 * @param maxDepth - Maximum depth to display
 * @param indentSize - Number of spaces for indentation
 * @param showRelationship - Whether to show relationship labels
 * @returns Formatted tree string
 */
function buildTreeString(
  node: string,
  childrenMap: Map<string, Array<{ target: string; relationship: string }>>,
  depth: number,
  maxDepth: number,
  indentSize: number,
  showRelationship: boolean
): string {
  // Start with the current node
  let result = `${' '.repeat(depth * indentSize)}${chalk.green(node)}\n`;
  
  // Return if we've reached the maximum depth or this node has no children
  if (depth >= maxDepth || !childrenMap.has(node)) {
    return result;
  }
  
  // Add each child node
  const children = childrenMap.get(node) || [];
  for (const { target, relationship } of children) {
    const relationshipText = showRelationship ? ` (${chalk.blue(relationship)})` : '';
    result += `${' '.repeat((depth + 1) * indentSize)}├── ${chalk.green(target)}${relationshipText}\n`;
    
    // Add the child's children if any
    if (childrenMap.has(target) && depth + 1 < maxDepth) {
      result += buildTreeString(target, childrenMap, depth + 2, maxDepth, indentSize, showRelationship);
    }
  }
  
  return result;
}

/**
 * Format output as plain text
 * 
 * @param data - Data to format
 * @returns Formatted plain text string
 */
export function formatAsPlain(data: any[]): string {
  return data.map(item => formatValue(item)).join('\n');
}

/**
 * Format a value for display
 * 
 * @param value - Value to format
 * @returns Formatted value
 */
function formatValue(value: any): string {
  if (value === undefined || value === null) {
    return '';
  }
  
  if (typeof value === 'object') {
    if (Array.isArray(value)) {
      return value.map(formatValue).join(', ');
    }
    return JSON.stringify(value);
  }
  
  return String(value);
}

/**
 * Format a query result based on the specified format
 * 
 * @param result - Query result to format
 * @param format - Output format
 * @returns Formatted result string
 */
export function formatOutput(result: QueryResult, format: OutputFormat): string {
  if (!result) {
    return 'No results to display';
  }
  
  switch (format) {
    case 'json':
      return formatAsJSON(result);
      
    case 'table':
      if ('keys' in result) { // CustomQueryResult
        const customResult = result as CustomQueryResult;
        const data = customResult.records.map(record => {
          const obj: Record<string, any> = {};
          customResult.keys.forEach(key => {
            obj[key] = record[key];
          });
          return obj;
        });
        return formatAsTable(data, customResult.keys);
      } else if ('records' in result) {
        if ('source' in result.records[0]) { // FileDependencyResult
          const depResult = result as FileDependencyResult;
          const keys = Object.keys(depResult.records[0]);
          return formatAsTable(depResult.records, keys);
        } else if ('path' in result.records[0]) { // PathQueryResult
          const pathResult = result as PathQueryResult;
          const data = pathResult.records.map(record => ({
            path: record.path.join(' → '),
            length: record.length
          }));
          return formatAsTable(data, ['path', 'length']);
        } else if ('count' in result.records[0]) { // FileStatResult
          const statResult = result as FileStatResult;
          const keys = Object.keys(statResult.records[0]);
          return formatAsTable(statResult.records, keys);
        }
      }
      
      // Default table fallback for unknown structure
      return 'Unable to format result as table: unknown structure';
    
    case 'tree':
      if (isFileDependencyResult(result)) {
        return formatAsTree(result);
      }
      return 'Tree format is only available for dependency results';
      
    case 'plain':
    default:
      if ('records' in result) {
        return formatAsPlain(result.records);
      }
      return formatAsJSON(result);
  }
}

/**
 * Type guard for FileDependencyResult
 * 
 * @param result - Query result to check
 * @returns Whether the result is a FileDependencyResult
 */
function isFileDependencyResult(result: QueryResult): result is FileDependencyResult {
  return 'records' in result && 
         result.records.length > 0 && 
         'source' in result.records[0] && 
         'target' in result.records[0];
}

/**
 * Format a status message with color
 * 
 * @param message - Message to format
 * @param status - Status type
 * @returns Formatted status message
 */
export function formatStatus(message: string, status: CommandStatus): string {
  switch (status) {
    case 'success':
      return chalk.green(`✓ ${message}`);
    case 'error':
      return chalk.red(`✗ ${message}`);
    case 'warning':
      return chalk.yellow(`⚠ ${message}`);
    case 'info':
    default:
      return chalk.blue(`ℹ ${message}`);
  }
}

export default {
  formatAsTable,
  formatAsJSON,
  formatAsTree,
  formatAsPlain,
  formatOutput,
  formatStatus,
}; 