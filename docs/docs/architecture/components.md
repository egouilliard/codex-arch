# Architecture Components

This document provides detailed information about each major component in the Codex-Arch architecture, their responsibilities, and how they interact with each other.

## Core Components

### Extractors

Extractors are responsible for parsing the codebase and extracting relevant structural information.

#### File Tree Extractor

The File Tree Extractor maps the directory and file structure of the codebase.

**Responsibilities:**
- Traverse directory structures
- Apply include/exclude filters
- Collect file metadata (size, modification time, etc.)
- Generate hierarchical file tree representation

**Key Classes:**
- `FileTreeExtractor`: Main extraction class
- `FileNode`: Represents a file in the tree
- `DirectoryNode`: Represents a directory in the tree

**Inputs and Outputs:**
- Input: Path to a directory
- Output: Hierarchical tree structure of files and directories

**Configuration Options:**
- `exclude_patterns`: List of glob patterns to exclude
- `max_depth`: Maximum directory depth to traverse
- `follow_symlinks`: Whether to follow symbolic links
- `include_hidden`: Whether to include hidden files/dirs

#### Python Dependency Extractor

The Python Dependency Extractor analyzes Python files to identify import statements and their dependencies.

**Responsibilities:**
- Parse Python source files
- Extract import statements
- Resolve import paths to actual files
- Build dependency relationships between modules

**Key Classes:**
- `PythonDependencyExtractor`: Main extraction class
- `ImportStatement`: Represents a parsed import statement
- `ModuleDependency`: Represents a dependency relationship

**Inputs and Outputs:**
- Input: Path to Python file(s) or directory
- Output: Graph of module dependencies

**Configuration Options:**
- `resolve_external`: Whether to resolve external dependencies
- `include_stdlib`: Whether to include standard library imports
- `analyze_comments`: Whether to check for imports in comments
- `aliases`: Dictionary of import aliases to resolve

#### Code Structure Extractor

The Code Structure Extractor analyzes code to identify classes, functions, and other structural elements.

**Responsibilities:**
- Parse code files
- Extract structural elements (classes, functions, etc.)
- Determine relationships between elements
- Calculate basic metrics (size, complexity, etc.)

**Key Classes:**
- `CodeStructureExtractor`: Main extraction class
- `CodeElement`: Base class for code elements
- `ClassElement`: Represents a class in the code
- `FunctionElement`: Represents a function/method

**Inputs and Outputs:**
- Input: Path to code file(s) or directory
- Output: Hierarchical structure of code elements

**Configuration Options:**
- `include_docstrings`: Include docstrings in the analysis
- `analyze_complexity`: Calculate complexity metrics
- `include_private`: Include private members
- `parse_type_hints`: Extract type hints from annotations

### Analyzers

Analyzers process the extracted information to generate insights and higher-level representations.

#### Dependency Analyzer

The Dependency Analyzer processes extracted dependency information to build a comprehensive dependency graph.

**Responsibilities:**
- Build a directed graph of dependencies
- Identify circular dependencies
- Calculate dependency metrics (fan-in, fan-out, etc.)
- Detect unused or orphaned modules

**Key Classes:**
- `DependencyAnalyzer`: Main analyzer class
- `DependencyGraph`: Graph representation of dependencies
- `DependencyMetrics`: Metrics calculator for dependencies

**Inputs and Outputs:**
- Input: Raw dependency data from extractors
- Output: Processed dependency graph with metrics

**Configuration Options:**
- `detect_cycles`: Whether to detect circular dependencies
- `include_external`: Include external dependencies in analysis
- `group_by_package`: Group modules by package in the graph

#### Code Structure Analyzer

The Code Structure Analyzer processes extracted code structure information to identify patterns and architectural elements.

**Responsibilities:**
- Identify architectural patterns
- Calculate structural metrics
- Detect code smells and anti-patterns
- Generate high-level architecture representations

**Key Classes:**
- `CodeStructureAnalyzer`: Main analyzer class
- `ArchitecturePattern`: Represents a detected pattern
- `CodeSmell`: Represents a potential code issue

**Inputs and Outputs:**
- Input: Raw code structure data from extractors
- Output: Processed structure analysis with metrics and patterns

**Configuration Options:**
- `patterns_to_detect`: List of patterns to look for
- `calculate_metrics`: List of metrics to calculate
- `detect_smells`: Whether to detect code smells

#### Change Analyzer

The Change Analyzer detects and analyzes changes between different versions of the codebase.

**Responsibilities:**
- Identify changed files between versions
- Analyze the impact of changes
- Calculate change-related metrics
- Generate change summaries

**Key Classes:**
- `ChangeAnalyzer`: Main analyzer class
- `ChangeSet`: Represents a set of changes
- `ChangedFile`: Represents a changed file
- `ChangeImpact`: Represents the impact of a change

**Inputs and Outputs:**
- Input: Two versions of the codebase and/or Git history
- Output: Analysis of changes and their impact

**Configuration Options:**
- `diff_algorithm`: Algorithm to use for diffing
- `analyze_impact`: Whether to analyze change impact
- `use_git`: Whether to use Git history for change detection

### Metrics Collectors

Metrics Collectors calculate various code metrics based on the extracted and analyzed information.

#### Size Metrics

Size Metrics calculate code size-related metrics.

**Responsibilities:**
- Count lines of code (total, non-blank, comment, etc.)
- Count files, classes, functions, etc.
- Calculate size distributions

**Key Classes:**
- `SizeMetricsCollector`: Main metrics class
- `FileMetrics`: Size metrics for a file
- `ProjectMetrics`: Aggregated size metrics

**Inputs and Outputs:**
- Input: Extracted code structure and file tree data
- Output: Size metrics at various granularities

**Configuration Options:**
- `count_blank_lines`: Whether to count blank lines
- `count_comments`: Whether to count comment lines
- `include_generated`: Whether to include generated code

#### Complexity Metrics

Complexity Metrics calculate code complexity-related metrics.

**Responsibilities:**
- Calculate cyclomatic complexity
- Calculate cognitive complexity
- Calculate maintainability indices
- Identify complex code areas

**Key Classes:**
- `ComplexityMetricsCollector`: Main metrics class
- `FunctionComplexity`: Complexity metrics for a function
- `FileComplexity`: Aggregated complexity for a file

**Inputs and Outputs:**
- Input: Extracted code structure data
- Output: Complexity metrics at various granularities

**Configuration Options:**
- `complexity_types`: Types of complexity to calculate
- `thresholds`: Warning/error thresholds for metrics
- `per_function`: Whether to calculate metrics per function

#### Dependency Metrics

Dependency Metrics calculate dependency-related metrics.

**Responsibilities:**
- Calculate coupling metrics (afferent, efferent)
- Calculate cohesion metrics
- Identify dependency hotspots
- Calculate modularity metrics

**Key Classes:**
- `DependencyMetricsCollector`: Main metrics class
- `ModuleCoupling`: Coupling metrics for a module
- `PackageCohesion`: Cohesion metrics for a package

**Inputs and Outputs:**
- Input: Processed dependency graph
- Output: Dependency metrics at various granularities

**Configuration Options:**
- `metrics_to_collect`: Types of metrics to calculate
- `granularity`: Level of granularity for metrics
- `normalize`: Whether to normalize metric values

### Visualization

Visualization components generate visual representations of the analyzed data.

#### Dependency Graph Generator

The Dependency Graph Generator creates visual representations of module dependencies.

**Responsibilities:**
- Generate dependency graphs in various formats
- Apply visual styling to nodes and edges
- Group and cluster related modules
- Add interactive elements (for HTML/SVG)

**Key Classes:**
- `DependencyGraphGenerator`: Main generator class
- `GraphStyler`: Handles visual styling
- `GraphRenderer`: Renders the graph in various formats

**Inputs and Outputs:**
- Input: Processed dependency graph
- Output: Visual representation in specified format (SVG, PNG, etc.)

**Configuration Options:**
- `format`: Output format (svg, png, dot, etc.)
- `direction`: Graph direction (LR, TB, RL, BT)
- `include_external`: Include external dependencies
- `cluster_by_package`: Group nodes by package

#### Structure Visualizer

The Structure Visualizer creates visual representations of code structure.

**Responsibilities:**
- Generate structure diagrams (class diagrams, etc.)
- Create treemaps and other hierarchical visualizations
- Add visual indicators for metrics
- Support interactive exploration

**Key Classes:**
- `StructureVisualizer`: Main visualizer class
- `ClassDiagramGenerator`: Generates class diagrams
- `TreemapGenerator`: Generates treemap visualizations

**Inputs and Outputs:**
- Input: Processed code structure data
- Output: Visual representation in specified format

**Configuration Options:**
- `diagram_type`: Type of diagram to generate
- `show_details`: Level of detail to include
- `color_scheme`: Color scheme for visualization

### Summary Builder

The Summary Builder creates comprehensive, human-readable summaries of the analysis.

**Responsibilities:**
- Aggregate analysis results
- Apply templates to generate reports
- Format data for various output formats
- Generate natural language summaries

**Key Classes:**
- `SummaryBuilder`: Main builder class
- `TemplateEngine`: Applies templates to data
- `ReportGenerator`: Generates complete reports
- `SummaryWriter`: Writes summaries in various formats

**Inputs and Outputs:**
- Input: Processed analysis data from all components
- Output: Formatted reports and summaries

**Configuration Options:**
- `format`: Output format (markdown, html, json, etc.)
- `templates`: Custom templates to use
- `sections`: Sections to include in the summary
- `detail_level`: Level of detail in the summary

## Integration Layer

### CLI Interface

The Command Line Interface provides command-line access to all Codex-Arch functionality.

**Responsibilities:**
- Parse command-line arguments
- Validate input and configuration
- Dispatch commands to appropriate components
- Display progress and results
- Handle errors and provide helpful messages

**Key Classes:**
- `CLI`: Main CLI class
- `CommandRegistry`: Registry of available commands
- `ProgressReporter`: Reports progress to the user
- `ErrorHandler`: Handles and formats errors

**Inputs and Outputs:**
- Input: Command-line arguments and options
- Output: Command execution results and status

**Configuration Options:**
- `verbosity`: Level of output verbosity
- `progress`: Whether to show progress indicators
- `color`: Whether to use colored output

### REST API

The REST API provides HTTP access to Codex-Arch functionality.

**Responsibilities:**
- Handle HTTP requests
- Authenticate and authorize clients
- Process API calls
- Return formatted responses
- Handle errors and exceptions

**Key Classes:**
- `APIServer`: Main server class
- `RequestHandler`: Processes API requests
- `ResponseFormatter`: Formats API responses
- `AuthenticationManager`: Handles authentication

**Inputs and Outputs:**
- Input: HTTP requests
- Output: HTTP responses with JSON data

**Configuration Options:**
- `host`: Host to bind to
- `port`: Port to listen on
- `auth`: Authentication configuration
- `cors`: CORS configuration

### Bundler

The Bundler packages analysis results into portable bundles.

**Responsibilities:**
- Collect analysis artifacts
- Create compressed archives
- Generate manifests
- Provide extraction and viewing capabilities

**Key Classes:**
- `BundleAssembler`: Main bundler class
- `ArtifactCollector`: Collects analysis artifacts
- `ManifestGenerator`: Generates bundle manifests
- `Compressor`: Compresses bundle contents

**Inputs and Outputs:**
- Input: Analysis results and artifacts
- Output: Compressed bundle with manifest

**Configuration Options:**
- `format`: Bundle format (zip, tar.gz, etc.)
- `include`: Types of artifacts to include
- `compression`: Compression level
- `manifest`: Whether to include a manifest

### Change Detection

The Change Detection module tracks and analyzes code changes over time.

**Responsibilities:**
- Detect changes between versions
- Trigger incremental analysis
- Cache and reuse previous results
- Generate change reports

**Key Classes:**
- `ChangeDetector`: Main detector class
- `GitChangeDetector`: Detects changes using Git
- `FileChangeDetector`: Detects changes by comparing files
- `ChangeCache`: Caches analysis results

**Inputs and Outputs:**
- Input: Previous and current code versions
- Output: Set of changes and incremental analysis results

**Configuration Options:**
- `detector`: Change detection method (git, file, etc.)
- `cache`: Cache configuration
- `incremental`: Whether to perform incremental analysis

## Extension Layer

### Git Hooks

Git Hooks automate analysis when code changes occur.

**Responsibilities:**
- Install Git hooks
- Trigger analysis on Git events
- Filter and process changed files
- Generate and display reports

**Key Classes:**
- `GitHookManager`: Manages Git hook installation
- `PreCommitHook`: Handles pre-commit events
- `PostMergeHook`: Handles post-merge events
- `HookConfigManager`: Manages hook configuration

**Inputs and Outputs:**
- Input: Git events and changed files
- Output: Analysis results and notifications

**Configuration Options:**
- `hooks`: Which hooks to install
- `triggers`: Events that trigger analysis
- `scope`: Analysis scope (changed files only, full project)

### Custom Processors

Custom Processors allow users to define custom analysis extensions.

**Responsibilities:**
- Load and execute custom scripts
- Provide access to analysis data
- Integrate custom results into main analysis
- Handle errors in custom code

**Key Classes:**
- `CustomProcessorManager`: Manages custom processors
- `ScriptProcessor`: Executes custom scripts
- `ProcessorContext`: Provides context to custom code
- `ResultIntegrator`: Integrates custom results

**Inputs and Outputs:**
- Input: Custom scripts and analysis data
- Output: Custom analysis results

**Configuration Options:**
- `processors`: List of custom processors to run
- `timeout`: Maximum execution time
- `sandbox`: Whether to run in a sandbox

### Export Adapters

Export Adapters convert analysis results to different formats.

**Responsibilities:**
- Transform analysis data to target format
- Apply format-specific optimizations
- Handle format-specific requirements
- Validate output correctness

**Key Classes:**
- `ExportManager`: Manages export adapters
- `JSONExporter`: Exports to JSON format
- `XMLExporter`: Exports to XML format
- `CustomExporter`: Base class for custom exporters

**Inputs and Outputs:**
- Input: Analysis results in internal format
- Output: Converted data in target format

**Configuration Options:**
- `format`: Target export format
- `pretty`: Whether to format output for readability
- `schema`: Schema to validate against (if applicable)

## Component Interaction Patterns

### Pipeline Processing

Many components interact through a pipeline pattern, where the output of one component becomes the input to the next.

**Example Pipeline:**
1. FileTreeExtractor extracts the file structure
2. PythonDependencyExtractor extracts dependencies
3. DependencyAnalyzer analyzes dependencies
4. DependencyMetricsCollector calculates metrics
5. DependencyGraphGenerator visualizes the results
6. SummaryBuilder includes results in final summary

### Observer Pattern

Some components use the observer pattern to notify other components of events.

**Example:**
- ChangeDetector notifies registered observers when changes are detected
- Observers like IncrementalAnalyzer respond to change events
- GitHooks observe Git events and trigger appropriate actions

### Strategy Pattern

Configuration options often use the strategy pattern to select different implementations.

**Example:**
- Different change detection strategies (Git-based, file-based)
- Different visualization rendering strategies (DOT, SVG, PNG)
- Different export format strategies (JSON, XML, custom)

### Facade Pattern

The CLI and API components serve as facades that simplify access to the complex underlying functionality.

**Example:**
- CLI Command `codex-arch analyze` orchestrates multiple extractors, analyzers, and other components
- API endpoint `/api/analyze` provides a simple interface to the same functionality

## Component Dependencies

The following diagram shows the high-level dependencies between major components:

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Extractors  │────▶│  Analyzers  │────▶│   Metrics    │────▶│ Visualization │
└─────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
       │                   │                   │                     │
       │                   │                   │                     │
       │                   ▼                   ▼                     ▼
       │            ┌───────────────────────────────────────────────────┐
       └───────────▶│                  Summary Builder                  │
                    └───────────────────────────────────────────────────┘
                                          │
                                          ▼
                    ┌───────────────────────────────────────────────────┐
                    │              Bundle Assembler                     │
                    └───────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
          ┌──────────────────┐  ┌─────────────────┐  ┌────────────────┐
          │   CLI Interface   │  │    REST API     │  │   Git Hooks    │
          └──────────────────┘  └─────────────────┘  └────────────────┘
```

## Next Steps

To learn more about how these components work together in typical workflows, see the [Workflow Examples](workflow.md) document. 