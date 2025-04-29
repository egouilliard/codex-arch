/**
 * Visualization utilities for the Codex-Arch CLI
 */

import fs from 'fs';
import path from 'path';
import open from 'open';
import { VisualizationOptions, FileDependencyResult, QueryResult } from '../types';

/**
 * Basic HTML template for visualizations
 */
const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Codex-Arch Visualization</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="https://unpkg.com/force-graph"></script>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f5f5f5;
    }
    #graph-container {
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }
    .controls {
      position: absolute;
      top: 10px;
      left: 10px;
      z-index: 10;
      background-color: rgba(255, 255, 255, 0.9);
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .legend {
      position: absolute;
      bottom: 10px;
      right: 10px;
      z-index: 10;
      background-color: rgba(255, 255, 255, 0.9);
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .color-square {
      display: inline-block;
      width: 12px;
      height: 12px;
      margin-right: 5px;
    }
  </style>
</head>
<body>
  <div id="graph-container"></div>
  <div class="controls">
    <h3>Codex-Arch Visualization</h3>
    <div>
      <label for="search">Search: </label>
      <input id="search" type="text" placeholder="Search for a file...">
    </div>
    <div>
      <label for="group-by">Group by: </label>
      <select id="group-by">
        <option value="none">None</option>
        <option value="directory">Directory</option>
      </select>
    </div>
    <div>
      <label for="link-strength">Link Strength: </label>
      <input id="link-strength" type="range" min="0" max="5" step="0.1" value="1">
    </div>
    <div>
      <button id="center">Center Graph</button>
      <button id="screenshot">Take Screenshot</button>
    </div>
  </div>
  <div class="legend" id="legend"></div>

  <script>
    // The data will be injected here
    const graphData = __GRAPH_DATA__;
    const vizType = '__VIZ_TYPE__';
    
    // Create the graph visualization
    const Graph = ForceGraph()(document.getElementById('graph-container'))
      .nodeId('id')
      .nodeLabel(node => node.label || node.id)
      .nodeColor(node => node.color || '#1f77b4')
      .nodeVal(node => node.value || 1)
      .linkSource('source')
      .linkTarget('target')
      .linkColor(link => link.color || '#999')
      .linkDirectionalArrowLength(4)
      .linkDirectionalArrowRelPos(1)
      .linkWidth(link => link.value || 1)
      .linkLabel(link => link.label || '')
      .graphData(graphData);
      
    // Add search functionality
    document.getElementById('search').addEventListener('input', e => {
      const searchTerm = e.target.value.toLowerCase();
      const nodes = Graph.graphData().nodes;
      
      if (searchTerm) {
        const matchedNodeIds = new Set(
          nodes
            .filter(node => node.id.toLowerCase().includes(searchTerm))
            .map(node => node.id)
        );
        
        Graph
          .nodeColor(node => matchedNodeIds.has(node.id) ? '#ff0000' : node.color || '#1f77b4')
          .nodeVal(node => matchedNodeIds.has(node.id) ? 5 : node.value || 1);
      } else {
        Graph
          .nodeColor(node => node.color || '#1f77b4')
          .nodeVal(node => node.value || 1);
      }
    });
    
    // Add group by functionality
    document.getElementById('group-by').addEventListener('change', e => {
      const groupBy = e.target.value;
      const nodes = Graph.graphData().nodes;
      
      if (groupBy === 'directory') {
        // Group by directory
        const directoryColors = {};
        let colorIndex = 0;
        const colors = [
          '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ];
        
        // Create legend for directories
        const legend = document.getElementById('legend');
        legend.innerHTML = '<h4>Directories</h4>';
        
        nodes.forEach(node => {
          const directory = node.id.split('/').slice(0, -1).join('/');
          
          if (!directoryColors[directory]) {
            directoryColors[directory] = colors[colorIndex % colors.length];
            colorIndex++;
            
            // Add to legend
            const item = document.createElement('div');
            item.innerHTML = '<span class="color-square" style="background-color: ' + directoryColors[directory] + '"></span>' + (directory || '(root)');
            legend.appendChild(item);
          }
          
          node.color = directoryColors[directory];
        });
        
        Graph.nodeColor(node => node.color);
      } else {
        // Reset colors
        nodes.forEach(node => {
          node.color = node.originalColor || '#1f77b4';
        });
        
        Graph.nodeColor(node => node.color);
        document.getElementById('legend').innerHTML = '';
      }
    });
    
    // Add link strength adjustment
    document.getElementById('link-strength').addEventListener('input', e => {
      const strength = parseFloat(e.target.value);
      Graph.d3Force('link').strength(strength);
    });
    
    // Add center button
    document.getElementById('center').addEventListener('click', () => {
      Graph.zoomToFit(400);
    });
    
    // Add screenshot button
    document.getElementById('screenshot').addEventListener('click', () => {
      const canvas = document.querySelector('canvas');
      const link = document.createElement('a');
      link.download = 'codex-arch-visualization.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
    
    // Initial zoom to fit
    Graph.zoomToFit(400, 100);
  </script>
</body>
</html>
`;

/**
 * Convert file dependency data to graph visualization data
 * 
 * @param data - File dependency data
 * @param options - Visualization options
 * @returns Graph visualization data
 */
function convertDependenciesToGraph(
  data: FileDependencyResult,
  options: VisualizationOptions
): { nodes: any[]; links: any[] } {
  const { maxDepth = Infinity, maxNodes } = options.options || {};
  
  // Extract nodes and links
  const nodesMap = new Map();
  const links: any[] = [];
  
  // Process records and create nodes and links
  data.records.forEach(record => {
    const { source, target, relationship, depth = 1 } = record;
    
    // Skip if beyond maximum depth
    if (depth > maxDepth) {
      return;
    }
    
    // Add source node if not already added
    if (!nodesMap.has(source)) {
      nodesMap.set(source, {
        id: source,
        label: path.basename(source),
        value: 1
      });
    } else {
      // Increment value for existing node
      nodesMap.get(source).value++;
    }
    
    // Add target node if not already added
    if (!nodesMap.has(target)) {
      nodesMap.set(target, {
        id: target,
        label: path.basename(target),
        value: 1
      });
    } else {
      // Increment value for existing node
      nodesMap.get(target).value++;
    }
    
    // Add link
    links.push({
      source,
      target,
      label: relationship,
      value: 1
    });
  });
  
  // Convert nodes map to array
  let nodes = Array.from(nodesMap.values());
  
  // Limit number of nodes if specified
  if (maxNodes && nodes.length > maxNodes) {
    // Sort nodes by value (importance) and take the top maxNodes
    nodes.sort((a, b) => b.value - a.value);
    nodes = nodes.slice(0, maxNodes);
    
    // Filter links to only include selected nodes
    const nodeIds = new Set(nodes.map(node => node.id));
    const filteredLinks = links.filter(link => 
      nodeIds.has(link.source) && nodeIds.has(link.target)
    );
    
    return { nodes, links: filteredLinks };
  }
  
  return { nodes, links };
}

/**
 * Generate visualization data from query results
 * 
 * @param data - Query result data
 * @param options - Visualization options
 * @returns Visualization data
 */
export function generateVisualizationData(
  data: QueryResult,
  options: VisualizationOptions
): { nodes: any[]; links: any[] } {
  switch (options.type) {
    case 'dependency-graph':
      if ('records' in data && data.records.length > 0 && 
          'source' in data.records[0] && 'target' in data.records[0]) {
        return convertDependenciesToGraph(data as FileDependencyResult, options);
      }
      throw new Error('Invalid data format for dependency graph visualization');
      
    case 'cluster-graph':
      // Implement cluster graph conversion logic
      throw new Error('Cluster graph visualization not implemented yet');
      
    case 'import-graph':
      if ('records' in data && data.records.length > 0 && 
          'source' in data.records[0] && 'target' in data.records[0]) {
        return convertDependenciesToGraph(data as FileDependencyResult, options);
      }
      throw new Error('Invalid data format for import graph visualization');
      
    default:
      throw new Error(`Unsupported visualization type: ${options.type}`);
  }
}

/**
 * Generate HTML visualization from query results
 * 
 * @param data - Query result data or pre-generated visualization data
 * @param options - Visualization options
 * @returns HTML content
 */
export function generateVisualization(
  data: QueryResult | { nodes: any[]; links: any[] },
  options: VisualizationOptions
): string {
  // Convert data to visualization format if it's a query result
  const graphData = 'nodes' in data
    ? data
    : generateVisualizationData(data as QueryResult, options);
  
  // Generate HTML from template
  let html = HTML_TEMPLATE;
  html = html.replace('__GRAPH_DATA__', JSON.stringify(graphData));
  html = html.replace('__VIZ_TYPE__', options.type);
  
  return html;
}

/**
 * Save visualization to a file
 * 
 * @param content - Visualization content
 * @param outputPath - Output file path
 * @returns Absolute path to the saved file
 */
export function saveVisualization(content: string, outputPath: string): string {
  // Create directory if it doesn't exist
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // Write content to file
  fs.writeFileSync(outputPath, content);
  
  return path.resolve(outputPath);
}

/**
 * Open visualization in the default browser
 * 
 * @param filePath - Path to the visualization file
 * @returns A promise that resolves when the browser is opened
 */
export async function openVisualization(filePath: string): Promise<void> {
  await open(filePath);
  return;
}

/**
 * Generate and save a visualization from query results
 * 
 * @param data - Query result data
 * @param options - Visualization options
 * @returns Absolute path to the saved file
 */
export async function createVisualization(
  data: QueryResult,
  options: VisualizationOptions
): Promise<string> {
  // Generate visualization content
  const content = generateVisualization(data, options);
  
  // Default output path if not specified
  const outputPath = options.outputPath || 
    `./outputs/visualizations/${options.type}-${Date.now()}.html`;
  
  // Save visualization
  const filePath = saveVisualization(content, outputPath);
  
  // Open in browser if requested
  if (options.openInBrowser) {
    await openVisualization(filePath);
  }
  
  return filePath;
}

export default {
  generateVisualizationData,
  generateVisualization,
  saveVisualization,
  openVisualization,
  createVisualization,
}; 