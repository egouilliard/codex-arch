# Visualization Module

The Visualization module generates visual representations of the codebase structure, dependencies, and metrics to help developers understand complex relationships and patterns that are difficult to grasp from text alone.

## Overview

The Visualization module consists of several components designed to create different types of visualizations:

- **Dependency Graph Generator**: Creates visual representations of module dependencies
- **Structure Visualizer**: Generates diagrams of code structure (classes, methods, etc.)
- **Metrics Visualizer**: Produces visual representations of code metrics
- **Treemap Generator**: Creates hierarchical treemap visualizations of the codebase

## Module Structure

```
visualization/
├── __init__.py         # Package exports
├── base.py             # Base visualization classes and interfaces
├── dependency.py       # Dependency graph visualization
├── structure.py        # Code structure visualization
├── metrics.py          # Metrics visualization
├── treemap.py          # Treemap visualization
├── renderers/          # Output format renderers
│   ├── __init__.py     # Renderer exports
│   ├── dot.py          # Graphviz DOT renderer
│   ├── svg.py          # SVG renderer
│   ├── html.py         # HTML interactive renderer
│   └── png.py          # PNG renderer
└── styles/             # Visual styling configuration
    ├── __init__.py     # Style exports
    ├── default.py      # Default styling
    ├── dark.py         # Dark theme styling
    └── colorblind.py   # Colorblind-friendly styling
```

## Key Components

### DependencyGraphGenerator

The `DependencyGraphGenerator` creates visual representations of module dependencies.

```python
from codex_arch.visualization import DependencyGraphGenerator

# Create a generator instance
generator = DependencyGraphGenerator(
    format="svg",
    direction="LR",
    cluster_by_package=True,
    include_external=False
)

# Generate a visualization from a dependency graph
dep_graph = dependency_analyzer.analyze_project("/path/to/project")
visualization = generator.generate(dep_graph)

# Save the visualization to a file
visualization.save("dependency-graph.svg")

# Apply a different style
from codex_arch.visualization.styles import DarkStyle
visualization.apply_style(DarkStyle())
visualization.save("dependency-graph-dark.svg")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `format` | Output format (svg, png, dot, html) | `"svg"` |
| `direction` | Graph direction (LR, TB, RL, BT) | `"LR"` |
| `cluster_by_package` | Group nodes by package | `True` |
| `include_external` | Include external dependencies | `False` |
| `max_depth` | Maximum depth of dependencies to show | `None` (unlimited) |
| `focus_modules` | List of modules to focus on | `None` (all modules) |

### StructureVisualizer

The `StructureVisualizer` generates diagrams of code structure, such as class diagrams.

```python
from codex_arch.visualization import StructureVisualizer

# Create a visualizer instance
visualizer = StructureVisualizer(
    diagram_type="class",
    show_methods=True,
    show_attributes=True,
    show_types=True
)

# Generate a visualization from code structure
code_structure = code_structure_extractor.extract("/path/to/project")
visualization = visualizer.generate(code_structure)

# Save the visualization
visualization.save("class-diagram.svg")

# Export as HTML with interactive features
visualization.export("class-diagram.html", renderer="html", interactive=True)
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `diagram_type` | Type of diagram (class, package, component) | `"class"` |
| `show_methods` | Whether to show methods | `True` |
| `show_attributes` | Whether to show attributes | `True` |
| `show_types` | Whether to show type information | `True` |
| `show_private` | Whether to show private members | `False` |
| `max_classes` | Maximum number of classes to show | `None` (unlimited) |

### MetricsVisualizer

The `MetricsVisualizer` produces visual representations of code metrics.

```python
from codex_arch.visualization import MetricsVisualizer

# Create a visualizer instance
visualizer = MetricsVisualizer(
    chart_type="bar",
    metrics=["complexity", "loc", "dependencies"],
    top_n=10,
    sort_by="complexity"
)

# Generate a visualization from metrics data
metrics = metrics_collector.collect("/path/to/project")
visualization = visualizer.generate(metrics)

# Save the visualization
visualization.save("metrics-chart.svg")

# Generate a different chart type
heatmap = visualizer.generate(
    metrics, 
    chart_type="heatmap", 
    metric="complexity"
)
heatmap.save("complexity-heatmap.svg")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `chart_type` | Type of chart (bar, line, radar, heatmap) | `"bar"` |
| `metrics` | List of metrics to visualize | `["complexity"]` |
| `top_n` | Number of top items to include | `10` |
| `sort_by` | Metric to sort by | `None` (no sorting) |
| `threshold_warning` | Warning threshold for color coding | `None` |
| `threshold_error` | Error threshold for color coding | `None` |

### TreemapGenerator

The `TreemapGenerator` creates hierarchical treemap visualizations of the codebase.

```python
from codex_arch.visualization import TreemapGenerator

# Create a generator instance
generator = TreemapGenerator(
    color_by="complexity",
    size_by="loc",
    max_depth=3,
    interactive=True
)

# Generate a treemap from file tree and metrics
file_tree = file_tree_extractor.extract("/path/to/project")
metrics = metrics_collector.collect("/path/to/project")
visualization = generator.generate(file_tree, metrics)

# Save the visualization
visualization.save("codebase-treemap.html")
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `color_by` | Metric to use for coloring | `"complexity"` |
| `size_by` | Metric to use for sizing | `"loc"` |
| `max_depth` | Maximum depth of hierarchy to show | `3` |
| `interactive` | Whether to create interactive visualization | `True` |
| `include_dirs` | Whether to include directories | `True` |
| `normalize_sizes` | Whether to normalize sizes | `True` |

## Usage in the Analysis Pipeline

The visualization module is typically used near the end of the analysis pipeline:

```python
from codex_arch.extractors import FileTreeExtractor, PythonDependencyExtractor
from codex_arch.analyzers import DependencyAnalyzer
from codex_arch.metrics import ComplexityMetricsCollector
from codex_arch.visualization import DependencyGraphGenerator, TreemapGenerator

# Extract and analyze the codebase
file_tree = FileTreeExtractor().extract("/path/to/project")
dependencies = PythonDependencyExtractor().extract_project("/path/to/project")
dep_graph = DependencyAnalyzer().analyze(dependencies)
metrics = ComplexityMetricsCollector().collect("/path/to/project")

# Generate visualizations
dep_vis = DependencyGraphGenerator().generate(dep_graph)
treemap = TreemapGenerator().generate(file_tree, metrics)

# Save visualizations
dep_vis.save("dependency-graph.svg")
treemap.save("complexity-treemap.html")

# Create a visualization bundle
from codex_arch.visualization import VisualizationBundle
bundle = VisualizationBundle()
bundle.add("dependencies", dep_vis)
bundle.add("complexity", treemap)
bundle.export("visualizations/")
```

## Renderers

The visualization module supports multiple output formats through different renderers:

### DOT Renderer

The DOT renderer generates Graphviz DOT files, which can be processed by Graphviz tools.

```python
from codex_arch.visualization.renderers import DotRenderer

# Create a renderer
renderer = DotRenderer(pretty_print=True)

# Render a visualization
dot_output = renderer.render(visualization)

# Save to a file
with open("graph.dot", "w") as f:
    f.write(dot_output)
```

### SVG Renderer

The SVG renderer generates SVG (Scalable Vector Graphics) files.

```python
from codex_arch.visualization.renderers import SVGRenderer

# Create a renderer
renderer = SVGRenderer(embed_styles=True)

# Render a visualization
svg_output = renderer.render(visualization)

# Save to a file
with open("graph.svg", "w") as f:
    f.write(svg_output)
```

### HTML Renderer

The HTML renderer generates interactive HTML visualizations.

```python
from codex_arch.visualization.renderers import HTMLRenderer

# Create a renderer
renderer = HTMLRenderer(
    interactive=True,
    include_scripts=True,
    template="default"
)

# Render a visualization
html_output = renderer.render(visualization)

# Save to a file
with open("graph.html", "w") as f:
    f.write(html_output)
```

## Styling

The visualization module provides flexible styling options:

```python
from codex_arch.visualization.styles import DefaultStyle

# Create a custom style based on the default
class CustomStyle(DefaultStyle):
    def __init__(self):
        super().__init__()
        self.node_color = "#4285f4"
        self.edge_color = "#999999"
        self.background_color = "#f8f9fa"
        self.font_family = "Arial, sans-serif"
        self.node_shape = "box"
        
# Apply the custom style
visualization.apply_style(CustomStyle())
```

## API Reference

For a complete API reference, see the auto-generated [API documentation](../api/visualization.md).

## Relevant Files

The main implementation files for the visualization module:

- `codex_arch/visualization/__init__.py`: Package exports
- `codex_arch/visualization/dependency.py`: Dependency graph visualization
- `codex_arch/visualization/structure.py`: Code structure visualization
- `codex_arch/visualization/metrics.py`: Metrics visualization
- `codex_arch/visualization/treemap.py`: Treemap visualization
- `codex_arch/visualization/renderers/`: Output format renderers
- `codex_arch/visualization/styles/`: Visual styling configuration

## Configuration Examples

### Example 1: Configuring Visualization in a Configuration File

```yaml
# codex-arch.yml
visualization:
  dependency_graph:
    format: "svg"
    direction: "LR"
    cluster_by_package: true
    include_external: false
    style:
      node:
        shape: "box"
        color: "#4285f4"
      edge:
        color: "#999999"
        style: "solid"
      cluster:
        color: "#e0e0e0"
        style: "dashed"
        
  structure:
    diagram_type: "class"
    show_methods: true
    show_attributes: true
    show_types: true
    show_private: false
    style:
      node:
        shape: "ellipse"
        color: "#34a853"
      edge:
        color: "#666666"
        
  metrics:
    chart_type: "bar"
    metrics:
      - "complexity"
      - "loc"
      - "dependencies"
    top_n: 15
    sort_by: "complexity"
    
  treemap:
    color_by: "complexity"
    size_by: "loc"
    max_depth: 4
    interactive: true
    normalize_sizes: true
```

### Example 2: Using Visualization from the Command Line

```bash
# Generate a dependency graph
codex-arch visualize dependency --format=svg --direction=LR /path/to/project

# Generate a class diagram
codex-arch visualize structure --diagram=class --show-methods --show-attributes /path/to/project

# Generate a metrics chart
codex-arch visualize metrics --chart=bar --metrics=complexity,loc --top=10 /path/to/project

# Generate a treemap
codex-arch visualize treemap --color-by=complexity --size-by=loc --interactive /path/to/project

# Generate all visualizations
codex-arch visualize all --output=visualizations/ /path/to/project
```

## Best Practices

- Choose the right visualization type for the information you want to convey
- Limit the complexity of visualizations to maintain readability
- Use color coding consistently and meaningfully
- Consider accessibility when choosing colors and shapes
- Provide interactive visualizations for complex codebases
- Include legends and explanations for non-obvious visual elements
- Use visualizations to complement textual analysis, not replace it 