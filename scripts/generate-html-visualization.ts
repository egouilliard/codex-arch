import fs from 'fs';
import path from 'path';

function generateHTML() {
  try {
    // Create output directory if it doesn't exist
    const outputDir = path.join(process.cwd(), 'outputs', 'visualizations');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Read the visualization data
    const dataPath = path.join(outputDir, 'typescript-visualization-data.json');
    if (!fs.existsSync(dataPath)) {
      throw new Error(`Visualization data file not found at ${dataPath}. Run the visualization script first.`);
    }
    
    console.log(`Reading visualization data from ${dataPath}...`);
    const graphData = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    
    // Generate the HTML - we'll use a string that contains a placeholder for the data
    // and then replace it to avoid template literal issues
    const htmlTemplate = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>TypeScript Repository Visualization</title>
  <style>
    body { 
      margin: 0; 
      font-family: Arial, sans-serif;
      overflow: hidden;
    }
    #container {
      position: relative;
      width: 100vw;
      height: 100vh;
    }
    .links line { 
      stroke: #999; 
      stroke-opacity: 0.6; 
    }
    .nodes circle { 
      stroke: #fff; 
      stroke-width: 1.5px; 
    }
    .node-labels { 
      font-size: 10px; 
      pointer-events: none;
    }
    .controls {
      position: absolute;
      top: 10px;
      left: 10px;
      background-color: rgba(255, 255, 255, 0.8);
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
      z-index: 100;
    }
    .controls button {
      margin: 5px;
      padding: 5px 10px;
      cursor: pointer;
    }
    .tooltip {
      position: absolute;
      padding: 10px;
      background-color: white;
      border-radius: 5px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
      pointer-events: none;
      opacity: 0;
    }
  </style>
</head>
<body>
  <div id="container">
    <div class="controls">
      <button id="zoom-in">+</button>
      <button id="zoom-out">-</button>
      <button id="reset">Reset</button>
      <div>
        <label for="group-by">Group by: </label>
        <select id="group-by">
          <option value="folder">Folder</option>
          <option value="extension">File Extension</option>
        </select>
      </div>
    </div>
    <div id="tooltip" class="tooltip"></div>
    <svg width="100%" height="100%"></svg>
  </div>
  
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script>
    // Visualization data
    const data = DATA_PLACEHOLDER;
    
    // Setup
    const svg = d3.select("svg");
    const width = svg.node().clientWidth;
    const height = svg.node().clientHeight;
    const tooltip = d3.select("#tooltip");
    
    // Create a color scale based on folder groups
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Create the visualization
    function createVisualization() {
      // Clear existing SVG content
      svg.selectAll("*").remove();
      
      // Add zoom behavior
      const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on("zoom", (event) => {
          g.attr("transform", event.transform);
        });
      
      svg.call(zoom);
      
      // Create main group for zooming
      const g = svg.append("g");
      
      // Create links
      const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
        .attr("stroke-width", d => Math.sqrt(d.value));
      
      // Create nodes
      const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", 8)
        .attr("fill", d => color(d.group))
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));
      
      // Add node labels
      const nodeLabels = g.append("g")
        .attr("class", "node-labels")
        .selectAll("text")
        .data(data.nodes)
        .enter().append("text")
        .text(d => d.name)
        .attr("dx", 12)
        .attr("dy", 4);
      
      // Show tooltip on hover
      node.on("mouseover", function(event, d) {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(\`<strong>\${d.name}</strong><br/>ID: \${d.id}<br/>Group: \${d.group}\`)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
      })
      .on("mouseout", function() {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
      });
      
      // Create a force simulation
      const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide(30));
      
      // Update positions on each tick
      simulation.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);
        
        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);
        
        nodeLabels
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      });
      
      // Drag functions
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      
      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }
      
      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
      
      // Setup controls
      d3.select("#zoom-in").on("click", () => {
        zoom.scaleBy(svg.transition().duration(750), 1.2);
      });
      
      d3.select("#zoom-out").on("click", () => {
        zoom.scaleBy(svg.transition().duration(750), 0.8);
      });
      
      d3.select("#reset").on("click", () => {
        svg.transition().duration(750).call(
          zoom.transform,
          d3.zoomIdentity
        );
      });
      
      d3.select("#group-by").on("change", function() {
        const groupBy = this.value;
        
        // Update node grouping
        if (groupBy === 'extension') {
          data.nodes.forEach(node => {
            const extension = node.id.split('.').pop();
            node.group = extension || 'unknown';
          });
        } else {
          data.nodes.forEach(node => {
            node.group = node.id.split('/').slice(-2)[0];
          });
        }
        
        // Update node colors
        node.attr("fill", d => color(d.group));
        
        // Restart simulation
        simulation.alpha(0.3).restart();
      });
    }
    
    // Initial creation
    createVisualization();
    
    // Handle window resize
    window.addEventListener('resize', () => {
      createVisualization();
    });
  </script>
</body>
</html>
`;
    
    // Replace the placeholder with the actual data
    const html = htmlTemplate.replace('DATA_PLACEHOLDER', JSON.stringify(graphData));
    
    // Write the HTML file
    const htmlOutputPath = path.join(outputDir, 'typescript-visualization.html');
    fs.writeFileSync(htmlOutputPath, html);
    console.log(`HTML visualization saved to ${htmlOutputPath}`);
    
    console.log('HTML visualization generation completed successfully');
  } catch (error) {
    console.error('HTML generation failed:', error);
    process.exit(1);
  }
}

// Run the HTML generation
generateHTML(); 