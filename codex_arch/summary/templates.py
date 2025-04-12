"""
Summary Templates Module

This module contains templates for generating Markdown and JSON summaries
of codebase architecture.
"""

import os
from typing import Dict, Any, List, Optional

# Default Markdown template for the summary
DEFAULT_MARKDOWN_TEMPLATE = """
# Codebase Architecture Summary

## Project Overview

- **Repository Path**: {repo_path}
- **Generated**: {timestamp}
- **Total Files**: {total_files}
- **Total Lines**: {total_lines}

## Language Distribution

{language_distribution}

## Complexity Overview

{complexity_overview}

## Key Files

{key_files}

## Directory Structure

{directory_structure}

## Dependency Analysis

{dependency_analysis}

## Architecture Insights

{architecture_insights}

## Visualizations

{visualizations}
"""

# Template for language distribution section in Markdown
LANGUAGE_DISTRIBUTION_TEMPLATE = """
| Language | Files | Lines | Percentage |
|----------|-------|-------|------------|
{language_rows}
"""

# Template for complexity overview section in Markdown
COMPLEXITY_OVERVIEW_TEMPLATE = """
- **Average Complexity**: {avg_complexity:.2f}
- **Max Complexity**: {max_complexity:.2f} (in {max_complexity_file})
- **Total Complex Files**: {complex_files_count} (complexity > 10)

### Top Complex Files

| File | Complexity |
|------|------------|
{complex_files_rows}
"""

# Template for key files section in Markdown
KEY_FILES_TEMPLATE = """
| File | Lines | Description |
|------|-------|-------------|
{key_files_rows}
"""

# Template for dependency analysis section in Markdown
DEPENDENCY_ANALYSIS_TEMPLATE = """
### Highly Connected Modules

| Module | Incoming | Outgoing | Total |
|--------|----------|----------|-------|
{connected_modules_rows}

### Circular Dependencies

{circular_dependencies}
"""

# Template for architecture insights section in Markdown
ARCHITECTURE_INSIGHTS_TEMPLATE = """
- **Modularity Score**: {modularity_score:.2f}/10
- **Dependency Depth**: {dependency_depth}
- **Core Components**: {core_components}
- **External Dependencies**: {external_dependencies}
"""

# Template for visualizations section in Markdown
VISUALIZATIONS_TEMPLATE = """
- [Dependency Graph](./dependencies.svg)
- [Module Structure](./module_structure.svg)
"""


class TemplateRenderer:
    """
    Template Renderer for Summary Generation

    Renders Markdown and JSON summaries based on the collected data.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize the TemplateRenderer.
        
        Args:
            data: The collected data to use for rendering
        """
        self.data = data
        self.output_dir = data.get('output_dir', os.path.join(os.getcwd(), 'output'))
    
    def _generate_language_distribution(self) -> str:
        """
        Generate the language distribution section of the summary.

        Returns:
            Rendered language distribution in Markdown format
        """
        if not self.data.get('metrics') or 'language_stats' not in self.data['metrics']:
            return "*No language distribution data available.*"
        
        language_stats = self.data['metrics']['language_stats']
        total_files = sum(stat.get('files', 0) for stat in language_stats.values())
        total_lines = sum(stat.get('lines', 0) for stat in language_stats.values())
        
        # Format the language distribution table rows
        rows = []
        for lang, stats in language_stats.items():
            if not stats.get('files', 0):
                continue
                
            percentage = (stats.get('lines', 0) / total_lines) * 100 if total_lines else 0
            row = f"| {lang} | {stats.get('files', 0)} | {stats.get('lines', 0)} | {percentage:.2f}% |"
            rows.append(row)
        
        # Sort by number of lines (descending)
        rows.sort(key=lambda x: float(x.split('|')[3].strip().replace('%', '')), reverse=True)
        
        return LANGUAGE_DISTRIBUTION_TEMPLATE.format(language_rows="\n".join(rows))
    
    def _generate_complexity_overview(self) -> str:
        """
        Generate the complexity overview section of the summary.

        Returns:
            Rendered complexity overview in Markdown format
        """
        if not self.data.get('metrics') or 'complexity' not in self.data['metrics']:
            return "*No complexity data available.*"
        
        complexity_data = self.data['metrics']['complexity']
        
        if not complexity_data or 'files' not in complexity_data:
            return "*No detailed complexity data available.*"
        
        avg_complexity = complexity_data.get('average', 0)
        max_complexity = 0
        max_complexity_file = ""
        complex_files = []
        
        # Find max complexity and complex files
        for file_path, file_data in complexity_data['files'].items():
            complexity = file_data.get('complexity', 0)
            
            if complexity > max_complexity:
                max_complexity = complexity
                max_complexity_file = file_path
            
            if complexity > 10:  # Threshold for "complex" files
                complex_files.append((file_path, complexity))
        
        # Sort complex files by complexity (descending)
        complex_files.sort(key=lambda x: x[1], reverse=True)
        
        # Cap to top 10
        complex_files = complex_files[:10]
        
        # Format complex files table rows
        complex_files_rows = "\n".join([
            f"| {file_path} | {complexity:.2f} |" 
            for file_path, complexity in complex_files
        ])
        
        return COMPLEXITY_OVERVIEW_TEMPLATE.format(
            avg_complexity=avg_complexity,
            max_complexity=max_complexity,
            max_complexity_file=max_complexity_file,
            complex_files_count=len(complex_files),
            complex_files_rows=complex_files_rows
        )
    
    def _generate_key_files(self) -> str:
        """
        Generate the key files section of the summary.

        Returns:
            Rendered key files section in Markdown format
        """
        if not self.data.get('metrics') or 'file_stats' not in self.data['metrics']:
            return "*No key files data available.*"
        
        file_stats = self.data['metrics']['file_stats']
        
        # Sort files by lines of code (descending)
        sorted_files = sorted(
            [(path, stats) for path, stats in file_stats.items()],
            key=lambda x: x[1].get('lines', 0),
            reverse=True
        )
        
        # Take the top 10 files
        key_files = sorted_files[:10]
        
        # Create table rows
        key_files_rows = []
        for file_path, stats in key_files:
            # Create a simple description based on file path and size
            description = f"{os.path.basename(file_path)} - {stats.get('type', 'Unknown')} file"
            lines = stats.get('lines', 0)
            
            key_files_rows.append(f"| {file_path} | {lines} | {description} |")
        
        return KEY_FILES_TEMPLATE.format(key_files_rows="\n".join(key_files_rows))
    
    def _generate_directory_structure(self) -> str:
        """
        Generate the directory structure section of the summary.

        Returns:
            Rendered directory structure in Markdown format
        """
        if not self.data.get('file_tree'):
            return "*No directory structure data available.*"
        
        # Use the Markdown representation from the file tree extractor if available
        file_tree = self.data.get('file_tree', {})
        
        if 'markdown' in file_tree:
            return file_tree['markdown']
        
        # Otherwise, create a simpler representation
        structure = "```\n"
        structure += self._format_dir_structure(file_tree)
        structure += "```"
        
        return structure
    
    def _format_dir_structure(self, node: Dict[str, Any], prefix: str = "", is_last: bool = True) -> str:
        """
        Format a directory structure node as a string.

        Args:
            node: Directory structure node
            prefix: Prefix for the current line
            is_last: Whether this is the last item in the current level

        Returns:
            Formatted directory structure as string
        """
        result = ""
        
        if not node:
            return result
            
        # Use name or default to 'root'
        name = node.get('name', 'root')
        
        # Determine the prefix for this line
        line_prefix = prefix + ("└── " if is_last else "├── ")
        
        # Add the line for this node
        result += f"{line_prefix}{name}\n"
        
        # Determine the prefix for children
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # Process children
        children = node.get('children', [])
        if children:
            for i, child in enumerate(children):
                child_is_last = (i == len(children) - 1)
                result += self._format_dir_structure(child, child_prefix, child_is_last)
        
        return result
    
    def _generate_dependency_analysis(self) -> str:
        """
        Generate the dependency analysis section of the summary.

        Returns:
            Rendered dependency analysis in Markdown format
        """
        if not self.data.get('python_dependencies'):
            return "*No dependency data available.*"
        
        dependencies = self.data.get('python_dependencies', {})
        
        # Extract modules and their dependency counts
        modules = {}
        for source, targets in dependencies.get('dependencies', {}).items():
            if source not in modules:
                modules[source] = {'incoming': 0, 'outgoing': len(targets)}
            else:
                modules[source]['outgoing'] = len(targets)
            
            # Count incoming dependencies
            for target in targets:
                if target not in modules:
                    modules[target] = {'incoming': 1, 'outgoing': 0}
                else:
                    modules[target]['incoming'] += 1
        
        # Calculate total connections
        for module, counts in modules.items():
            counts['total'] = counts['incoming'] + counts['outgoing']
        
        # Sort by total connections (descending)
        connected_modules = sorted(
            [(m, c) for m, c in modules.items()],
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        # Take the top 10 most connected modules
        connected_modules = connected_modules[:10]
        
        # Format connected modules table
        connected_modules_rows = []
        for module, counts in connected_modules:
            row = f"| {module} | {counts['incoming']} | {counts['outgoing']} | {counts['total']} |"
            connected_modules_rows.append(row)
        
        # Check for circular dependencies
        circular_deps = dependencies.get('circular_dependencies', [])
        
        if circular_deps:
            circular_dependencies = "Detected circular dependencies:\n\n"
            for cycle in circular_deps:
                circular_dependencies += f"- {' → '.join(cycle)} → {cycle[0]}\n"
        else:
            circular_dependencies = "No circular dependencies detected."
        
        return DEPENDENCY_ANALYSIS_TEMPLATE.format(
            connected_modules_rows="\n".join(connected_modules_rows),
            circular_dependencies=circular_dependencies
        )
    
    def _generate_architecture_insights(self) -> str:
        """
        Generate the architecture insights section of the summary.

        Returns:
            Rendered architecture insights in Markdown format
        """
        # Calculate a simple modularity score (0-10) based on metrics we have
        # This is a very simplified metric and could be improved
        modularity_score = 5.0  # Default middle score
        
        dependencies = self.data.get('python_dependencies', {})
        if dependencies:
            # Look at number of circular dependencies (fewer is better)
            circular_deps = dependencies.get('circular_dependencies', [])
            if circular_deps:
                modularity_score -= min(len(circular_deps), 3)  # Deduct up to 3 points
            else:
                modularity_score += 1  # Bonus for no circular dependencies
            
            # Calculate dependency depth
            max_depth = 0
            module_deps = dependencies.get('dependencies', {})
            if module_deps:
                # This is a very simplified calculation
                # In a real analysis we would do a topological sort
                max_depth = max(len(deps) for deps in module_deps.values()) if module_deps else 0
        else:
            max_depth = "Unknown"
        
        # Identify core components based on connectivity
        if hasattr(self, '_generate_dependency_analysis'):
            # Extract from dependency analysis
            core_components = []
            if dependencies and 'dependencies' in dependencies:
                module_deps = dependencies['dependencies']
                # Modules with most incoming dependencies are likely core components
                incoming_counts = {}
                for source, targets in module_deps.items():
                    for target in targets:
                        incoming_counts[target] = incoming_counts.get(target, 0) + 1
                
                # Get top 3 modules by incoming dependencies
                top_modules = sorted(
                    [(m, c) for m, c in incoming_counts.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                core_components = [m for m, _ in top_modules]
        
        if not core_components:
            core_components = "None identified"
        else:
            core_components = ", ".join(core_components)
        
        # Get external dependencies from Python dependencies
        external_deps = []
        if self.data.get('metrics') and 'dependencies' in self.data['metrics']:
            external_deps = self.data['metrics']['dependencies'].get('external', [])
        
        if not external_deps:
            external_dependencies = "None detected"
        else:
            # Take top 5 external dependencies
            external_dependencies = ", ".join(external_deps[:5])
            if len(external_deps) > 5:
                external_dependencies += f" and {len(external_deps) - 5} more"
        
        return ARCHITECTURE_INSIGHTS_TEMPLATE.format(
            modularity_score=modularity_score,
            dependency_depth=max_depth,
            core_components=core_components,
            external_dependencies=external_dependencies
        )
    
    def _generate_visualizations(self) -> str:
        """
        Generate the visualizations section of the summary.

        Returns:
            Rendered visualizations section in Markdown format
        """
        visualizations = self.data.get('visualizations', [])
        
        if not visualizations:
            return "*No visualizations available.*"
        
        # Create links for each visualization
        vis_links = []
        for vis_path in visualizations:
            if not vis_path:
                continue
                
            # Get the file name
            vis_name = os.path.basename(vis_path)
            
            # Determine the visualization type from extension
            vis_type = "Dependency Graph"
            if "module" in vis_name:
                vis_type = "Module Structure"
            elif "tree" in vis_name:
                vis_type = "Directory Tree"
            
            vis_links.append(f"- [{vis_type}](./{vis_name})")
        
        if not vis_links:
            return "*No visualizations available.*"
            
        return "\n".join(vis_links)
    
    def render_markdown(self) -> str:
        """
        Render the complete Markdown summary.

        Returns:
            Complete Markdown summary
        """
        import datetime
        
        # Get basic metrics
        metrics = self.data.get('metrics', {})
        total_files = metrics.get('total_files', 0)
        total_lines = metrics.get('total_lines', 0)
        
        # Generate each section
        language_distribution = self._generate_language_distribution()
        complexity_overview = self._generate_complexity_overview()
        key_files = self._generate_key_files()
        directory_structure = self._generate_directory_structure()
        dependency_analysis = self._generate_dependency_analysis()
        architecture_insights = self._generate_architecture_insights()
        visualizations = self._generate_visualizations()
        
        # Format the complete template
        summary = DEFAULT_MARKDOWN_TEMPLATE.format(
            repo_path=self.data.get('repo_path', 'Unknown'),
            timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            total_files=total_files,
            total_lines=total_lines,
            language_distribution=language_distribution,
            complexity_overview=complexity_overview,
            key_files=key_files,
            directory_structure=directory_structure,
            dependency_analysis=dependency_analysis,
            architecture_insights=architecture_insights,
            visualizations=visualizations
        )
        
        return summary
    
    def render_json(self) -> Dict[str, Any]:
        """
        Render the JSON summary.

        Returns:
            Complete JSON summary as a dictionary
        """
        import datetime
        
        # Start with basic project info
        summary = {
            'repo_path': self.data.get('repo_path', 'Unknown'),
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': self.data.get('metrics', {}),
            'dependencies': self.data.get('python_dependencies', {}),
            'file_tree': self.data.get('file_tree', {}),
            'visualizations': self.data.get('visualizations', [])
        }
        
        # Add smart insights
        summary['insights'] = {
            'key_files': [],
            'complex_files': [],
            'highly_connected_modules': [],
            'circular_dependencies': summary.get('dependencies', {}).get('circular_dependencies', [])
        }
        
        # Extract key files
        if 'metrics' in self.data and 'file_stats' in self.data['metrics']:
            file_stats = self.data['metrics']['file_stats']
            
            # Sort files by lines of code (descending)
            sorted_files = sorted(
                [(path, stats) for path, stats in file_stats.items()],
                key=lambda x: x[1].get('lines', 0),
                reverse=True
            )
            
            # Take the top 10 files
            key_files = sorted_files[:10]
            
            summary['insights']['key_files'] = [
                {
                    'path': path,
                    'lines': stats.get('lines', 0),
                    'type': stats.get('type', 'Unknown')
                }
                for path, stats in key_files
            ]
        
        # Extract complex files
        if 'metrics' in self.data and 'complexity' in self.data['metrics']:
            complexity_data = self.data['metrics']['complexity']
            
            if 'files' in complexity_data:
                complex_files = []
                
                for file_path, file_data in complexity_data['files'].items():
                    complexity = file_data.get('complexity', 0)
                    
                    if complexity > 10:  # Threshold for "complex" files
                        complex_files.append({
                            'path': file_path,
                            'complexity': complexity
                        })
                
                # Sort by complexity (descending)
                complex_files.sort(key=lambda x: x['complexity'], reverse=True)
                
                # Take top 10
                summary['insights']['complex_files'] = complex_files[:10]
        
        # Extract highly connected modules
        if 'python_dependencies' in self.data and 'dependencies' in self.data['python_dependencies']:
            module_deps = self.data['python_dependencies']['dependencies']
            
            # Calculate incoming and outgoing dependencies
            modules = {}
            for source, targets in module_deps.items():
                if source not in modules:
                    modules[source] = {'incoming': 0, 'outgoing': len(targets)}
                else:
                    modules[source]['outgoing'] = len(targets)
                
                # Count incoming dependencies
                for target in targets:
                    if target not in modules:
                        modules[target] = {'incoming': 1, 'outgoing': 0}
                    else:
                        modules[target]['incoming'] += 1
            
            # Calculate total connections
            for module, counts in modules.items():
                counts['total'] = counts['incoming'] + counts['outgoing']
            
            # Sort by total connections (descending)
            connected_modules = sorted(
                [(m, c) for m, c in modules.items()],
                key=lambda x: x[1]['total'],
                reverse=True
            )
            
            # Take the top 10 most connected modules
            connected_modules = connected_modules[:10]
            
            # Format for JSON
            summary['insights']['highly_connected_modules'] = [
                {
                    'module': module,
                    'incoming': counts['incoming'],
                    'outgoing': counts['outgoing'],
                    'total': counts['total']
                }
                for module, counts in connected_modules
            ]
        
        return summary
    
    def save_markdown(self, output_file: Optional[str] = None) -> str:
        """
        Render and save the Markdown summary to a file.

        Args:
            output_file: Output file path (defaults to 'output/summary.md')

        Returns:
            Path to the saved file
        """
        output_file = output_file or os.path.join(self.output_dir, 'summary.md')
        
        # Render the Markdown
        markdown = self.render_markdown()
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(markdown)
        
        return output_file
    
    def save_json(self, output_file: Optional[str] = None) -> str:
        """
        Render and save the JSON summary to a file.

        Args:
            output_file: Output file path (defaults to 'output/summary.json')

        Returns:
            Path to the saved file
        """
        import json
        
        output_file = output_file or os.path.join(self.output_dir, 'summary.json')
        
        # Render the JSON
        json_data = self.render_json()
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        return output_file 