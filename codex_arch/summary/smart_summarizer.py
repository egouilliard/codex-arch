"""
Smart Summarization Logic Module

This module analyzes code metrics and dependencies to provide
intelligent insights and highlights about the codebase architecture.
"""

from typing import Dict, Any, List, Optional, Tuple


class SmartSummarizer:
    """
    Smart Summarization Logic

    Analyzes code patterns and provides architectural insights based on
    metrics, dependencies, and code structure.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize the SmartSummarizer.

        Args:
            data: The collected data to analyze
        """
        self.data = data
        self.insights = {}

    def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analyze dependencies to identify patterns.

        Returns:
            Dictionary of dependency insights
        """
        insights = {
            'circular_dependencies': [],
            'highly_connected_modules': [],
            'isolated_modules': [],
            'core_components': [],
            'bottlenecks': []
        }

        # Skip if no dependency data
        if not self.data.get('python_dependencies'):
            return insights

        dependencies = self.data.get('python_dependencies', {})
        module_deps = dependencies.get('dependencies', {})

        if not module_deps:
            return insights

        # Extract circular dependencies
        insights['circular_dependencies'] = dependencies.get('circular_dependencies', [])

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

        # Calculate total connections and centrality
        for module, counts in modules.items():
            counts['total'] = counts['incoming'] + counts['outgoing']
            
            # A simple centrality measure (higher means more central)
            counts['centrality'] = counts['incoming'] * 2 + counts['outgoing']

        # Find highly connected modules (top 10% by total connections)
        connected_modules = sorted(
            [(m, c) for m, c in modules.items()],
            key=lambda x: x[1]['total'],
            reverse=True
        )
        
        # Take the top 10% or at least 5 modules
        top_count = max(5, int(len(connected_modules) * 0.1))
        insights['highly_connected_modules'] = [
            {
                'module': module,
                'incoming': counts['incoming'],
                'outgoing': counts['outgoing'],
                'total': counts['total']
            }
            for module, counts in connected_modules[:top_count]
        ]

        # Find isolated modules (no incoming connections)
        isolated_modules = [
            module for module, counts in modules.items()
            if counts['incoming'] == 0 and counts['outgoing'] > 0
        ]
        insights['isolated_modules'] = isolated_modules

        # Identify core components (high centrality)
        core_modules = sorted(
            [(m, c) for m, c in modules.items()],
            key=lambda x: x[1]['centrality'],
            reverse=True
        )
        
        # Take top 5 core modules
        insights['core_components'] = [
            {
                'module': module,
                'centrality': counts['centrality'],
                'incoming': counts['incoming'],
                'outgoing': counts['outgoing']
            }
            for module, counts in core_modules[:5]
        ]

        # Identify bottlenecks (high incoming, low outgoing)
        bottlenecks = []
        for module, counts in modules.items():
            # Simple heuristic for bottlenecks
            if counts['incoming'] > 2 and counts['outgoing'] <= 1:
                bottlenecks.append({
                    'module': module,
                    'incoming': counts['incoming'],
                    'outgoing': counts['outgoing']
                })
        
        # Sort by incoming connections
        bottlenecks.sort(key=lambda x: x['incoming'], reverse=True)
        insights['bottlenecks'] = bottlenecks[:5]  # Take top 5

        return insights

    def analyze_complexity(self) -> Dict[str, Any]:
        """
        Analyze code complexity to identify hotspots.

        Returns:
            Dictionary of complexity insights
        """
        insights = {
            'complex_files': [],
            'complex_modules': [],
            'average_complexity': 0.0,
            'complexity_distribution': {}
        }

        # Skip if no complexity data
        if not self.data.get('metrics') or 'complexity' not in self.data['metrics']:
            return insights

        complexity_data = self.data['metrics']['complexity']
        
        # Get average complexity
        insights['average_complexity'] = complexity_data.get('average', 0.0)
        
        # Identify complex files
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
            insights['complex_files'] = complex_files[:10]
            
            # Group files by module to find complex modules
            module_complexity = {}
            for file_path, file_data in complexity_data['files'].items():
                # Extract module name from file path
                # This is a simplistic approach - adjust based on your project structure
                parts = file_path.split('/')
                if len(parts) > 1:
                    module = parts[0]  # Use first directory as module
                    complexity = file_data.get('complexity', 0)
                    
                    if module not in module_complexity:
                        module_complexity[module] = {
                            'total_complexity': complexity,
                            'file_count': 1,
                            'complex_files': 1 if complexity > 10 else 0
                        }
                    else:
                        module_complexity[module]['total_complexity'] += complexity
                        module_complexity[module]['file_count'] += 1
                        if complexity > 10:
                            module_complexity[module]['complex_files'] += 1
            
            # Calculate average complexity per module
            for module, data in module_complexity.items():
                if data['file_count'] > 0:
                    data['average_complexity'] = data['total_complexity'] / data['file_count']
            
            # Sort modules by average complexity
            complex_modules = [
                {
                    'module': module,
                    'average_complexity': data['average_complexity'],
                    'total_complexity': data['total_complexity'],
                    'file_count': data['file_count'],
                    'complex_files': data['complex_files']
                }
                for module, data in module_complexity.items()
                if data['file_count'] >= 2  # Only include modules with at least 2 files
            ]
            
            complex_modules.sort(key=lambda x: x['average_complexity'], reverse=True)
            insights['complex_modules'] = complex_modules[:5]  # Take top 5
            
            # Create complexity distribution
            complexity_ranges = {
                'low': {'range': '0-5', 'count': 0},
                'medium': {'range': '5-10', 'count': 0},
                'high': {'range': '10-20', 'count': 0},
                'very_high': {'range': '20+', 'count': 0}
            }
            
            for file_data in complexity_data['files'].values():
                complexity = file_data.get('complexity', 0)
                
                if complexity < 5:
                    complexity_ranges['low']['count'] += 1
                elif complexity < 10:
                    complexity_ranges['medium']['count'] += 1
                elif complexity < 20:
                    complexity_ranges['high']['count'] += 1
                else:
                    complexity_ranges['very_high']['count'] += 1
            
            insights['complexity_distribution'] = complexity_ranges

        return insights

    def analyze_language_distribution(self) -> Dict[str, Any]:
        """
        Analyze language distribution.

        Returns:
            Dictionary of language distribution insights
        """
        insights = {
            'primary_language': None,
            'language_breakdown': [],
            'file_type_stats': []
        }

        # Skip if no language stats
        if not self.data.get('metrics') or 'language_stats' not in self.data['metrics']:
            return insights

        language_stats = self.data['metrics']['language_stats']
        
        # Calculate total files and lines
        total_files = sum(stat.get('files', 0) for stat in language_stats.values())
        total_lines = sum(stat.get('lines', 0) for stat in language_stats.values())
        
        # Create language breakdown
        language_breakdown = []
        for lang, stats in language_stats.items():
            if not stats.get('files', 0):
                continue
                
            percentage = (stats.get('lines', 0) / total_lines) * 100 if total_lines else 0
            language_breakdown.append({
                'language': lang,
                'files': stats.get('files', 0),
                'lines': stats.get('lines', 0),
                'percentage': percentage
            })
        
        # Sort by percentage (descending)
        language_breakdown.sort(key=lambda x: x['percentage'], reverse=True)
        insights['language_breakdown'] = language_breakdown
        
        # Determine primary language
        if language_breakdown:
            insights['primary_language'] = language_breakdown[0]['language']
        
        # Get file type stats
        if 'file_stats' in self.data['metrics']:
            file_stats = self.data['metrics']['file_stats']
            
            # Count files by extension
            extension_counts = {}
            for file_path in file_stats:
                # Extract file extension
                ext = file_path.split('.')[-1] if '.' in file_path else 'no_extension'
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
            
            # Sort by count (descending)
            file_type_stats = [
                {'extension': ext, 'count': count}
                for ext, count in extension_counts.items()
            ]
            file_type_stats.sort(key=lambda x: x['count'], reverse=True)
            
            insights['file_type_stats'] = file_type_stats

        return insights

    def analyze_architecture(self) -> Dict[str, Any]:
        """
        Analyze overall architecture.

        Returns:
            Dictionary of architecture insights
        """
        insights = {
            'modularity_score': 5.0,  # Default middle score
            'dependency_depth': 0,
            'architecture_type': 'Unknown',
            'recommendations': []
        }

        # Skip if no dependencies
        if not self.data.get('python_dependencies'):
            return insights

        dependencies = self.data.get('python_dependencies', {})
        module_deps = dependencies.get('dependencies', {})
        circular_deps = dependencies.get('circular_dependencies', [])

        if not module_deps:
            return insights

        # Calculate modularity score (0-10)
        modularity_score = 5.0  # Start with a middle score
        
        # Deduct for circular dependencies
        if circular_deps:
            modularity_score -= min(len(circular_deps), 3)  # Deduct up to 3 points
        else:
            modularity_score += 1  # Bonus for no circular dependencies
        
        # Calculate dependency graph stats
        in_degree = {}  # Number of incoming edges
        out_degree = {}  # Number of outgoing edges
        
        for source, targets in module_deps.items():
            if source not in out_degree:
                out_degree[source] = len(targets)
            else:
                out_degree[source] += len(targets)
            
            for target in targets:
                if target not in in_degree:
                    in_degree[target] = 1
                else:
                    in_degree[target] += 1
        
        # Find dependency depth (maximum path length)
        # This is a simplistic approach - for a real project, use a topological sort
        if module_deps:
            max_depth = max(len(deps) for deps in module_deps.values()) if module_deps else 0
            insights['dependency_depth'] = max_depth
        
        # Adjust modularity score based on dependency stats
        
        # High fan-in/fan-out ratio indicates potential modularity issues
        max_in_degree = max(in_degree.values()) if in_degree else 0
        max_out_degree = max(out_degree.values()) if out_degree else 0
        
        if max_in_degree > 10:
            modularity_score -= 1  # Deduct for high fan-in
        
        if max_out_degree > 10:
            modularity_score -= 1  # Deduct for high fan-out
        
        # Identify architecture type
        architecture_type = 'Unknown'
        
        # Count modules with no incoming dependencies (sources)
        sources = [m for m in module_deps.keys() if m not in in_degree or in_degree[m] == 0]
        
        # Count modules with no outgoing dependencies (sinks)
        sinks = [m for m in set(in_degree.keys()) if m not in out_degree or not module_deps.get(m)]
        
        # Simple heuristics for architecture types
        if len(sources) == 1 and max_out_degree > 5:
            architecture_type = 'Centralized (star/hub)'
        elif len(sources) > 3 and len(sinks) > 3 and max_in_degree < 5 and max_out_degree < 5:
            architecture_type = 'Layered/Pipeline'
        elif circular_deps:
            if len(circular_deps) > 3:
                architecture_type = 'Highly interconnected'
            else:
                architecture_type = 'Partially interconnected'
        elif max_in_degree < 3 and max_out_degree < 3:
            architecture_type = 'Modular/Component-based'
        
        insights['architecture_type'] = architecture_type
        
        # Generate recommendations based on findings
        recommendations = []
        
        if circular_deps:
            recommendations.append("Consider refactoring to eliminate circular dependencies for better maintainability.")
        
        if max_in_degree > 10:
            recommendations.append("Some modules have too many incoming dependencies. Consider breaking them down.")
        
        if max_out_degree > 10:
            recommendations.append("Some modules have too many outgoing dependencies. Consider employing dependency injection or abstractions.")
        
        if architecture_type == 'Highly interconnected':
            recommendations.append("The codebase is highly interconnected. Consider a more modular approach.")
        
        insights['modularity_score'] = max(0, min(10, modularity_score))  # Ensure within range 0-10
        insights['recommendations'] = recommendations

        return insights

    def analyze_hotspots(self) -> Dict[str, Any]:
        """
        Identify code hotspots that might need attention.

        Returns:
            Dictionary of hotspot insights
        """
        insights = {
            'complex_hotspots': [],
            'dependency_hotspots': []
        }

        # Skip if no complexity data
        if (not self.data.get('metrics') or 'complexity' not in self.data['metrics'] or
            not self.data.get('python_dependencies')):
            return insights

        complexity_data = self.data['metrics']['complexity']
        dependencies = self.data.get('python_dependencies', {})
        module_deps = dependencies.get('dependencies', {})
        
        if not 'files' in complexity_data or not module_deps:
            return insights
        
        # Identify complex files
        complex_files = []
        for file_path, file_data in complexity_data['files'].items():
            complexity = file_data.get('complexity', 0)
            
            if complexity > 10:  # Threshold for "complex" files
                complex_files.append((file_path, complexity))
        
        # Calculate incoming dependencies for modules
        module_in_degree = {}
        for source, targets in module_deps.items():
            for target in targets:
                module_in_degree[target] = module_in_degree.get(target, 0) + 1
        
        # Find complex files with high dependencies as hotspots
        # This is a simplistic approach - we're matching files to modules by prefix
        complex_hotspots = []
        for file_path, complexity in complex_files:
            # Extract module from file path
            parts = file_path.split('/')
            if len(parts) > 1:
                module = parts[0]  # Use first directory as module
                
                # Find if this module has high dependencies
                if module in module_in_degree and module_in_degree[module] > 2:
                    complex_hotspots.append({
                        'file': file_path,
                        'complexity': complexity,
                        'module': module,
                        'module_dependencies': module_in_degree[module]
                    })
        
        # Sort by a combined score of complexity and dependencies
        complex_hotspots.sort(
            key=lambda x: x['complexity'] * x['module_dependencies'], 
            reverse=True
        )
        
        insights['complex_hotspots'] = complex_hotspots[:5]  # Take top 5
        
        # Find modules with both high incoming and outgoing dependencies
        dependency_hotspots = []
        for module in set(module_deps.keys()) | set(module_in_degree.keys()):
            in_degree = module_in_degree.get(module, 0)
            out_degree = len(module_deps.get(module, []))
            
            # Modules with high connectivity in both directions are potential hotspots
            if in_degree > 2 and out_degree > 2:
                dependency_hotspots.append({
                    'module': module,
                    'incoming': in_degree,
                    'outgoing': out_degree,
                    'total': in_degree + out_degree
                })
        
        # Sort by total dependencies
        dependency_hotspots.sort(key=lambda x: x['total'], reverse=True)
        insights['dependency_hotspots'] = dependency_hotspots[:5]  # Take top 5

        return insights

    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate all insights.

        Returns:
            Complete dictionary of all insights
        """
        all_insights = {
            'dependencies': self.analyze_dependencies(),
            'complexity': self.analyze_complexity(),
            'language': self.analyze_language_distribution(),
            'architecture': self.analyze_architecture(),
            'hotspots': self.analyze_hotspots()
        }
        
        # Store the insights for later use
        self.insights = all_insights
        
        return all_insights

    def generate_summary_text(self) -> str:
        """
        Generate a textual summary of the insights.

        Returns:
            Human-readable summary text
        """
        # Ensure insights are generated
        if not self.insights:
            self.generate_insights()
        
        summary_parts = []
        
        # Architecture overview
        arch_insights = self.insights.get('architecture', {})
        arch_type = arch_insights.get('architecture_type', 'Unknown')
        mod_score = arch_insights.get('modularity_score', 0)
        dep_depth = arch_insights.get('dependency_depth', 0)
        
        summary_parts.append(f"## Architecture Overview\n\n")
        summary_parts.append(f"This codebase appears to have a **{arch_type}** architecture ")
        summary_parts.append(f"with a modularity score of **{mod_score:.1f}/10** and ")
        summary_parts.append(f"a maximum dependency depth of **{dep_depth}**.\n\n")
        
        # Language breakdown
        lang_insights = self.insights.get('language', {})
        primary_lang = lang_insights.get('primary_language', 'Unknown')
        lang_breakdown = lang_insights.get('language_breakdown', [])
        
        if primary_lang and lang_breakdown:
            summary_parts.append(f"## Language Distribution\n\n")
            summary_parts.append(f"The primary language is **{primary_lang}** ")
            
            if len(lang_breakdown) > 1:
                top_langs = [f"{lang['language']} ({lang['percentage']:.1f}%)" 
                            for lang in lang_breakdown[:3]]
                summary_parts.append(f"with a mix of {', '.join(top_langs)}.\n\n")
            else:
                summary_parts.append(f"({lang_breakdown[0]['percentage']:.1f}% of the codebase).\n\n")
        
        # Complexity highlights
        complex_insights = self.insights.get('complexity', {})
        avg_complexity = complex_insights.get('average_complexity', 0)
        complex_files = complex_insights.get('complex_files', [])
        complex_modules = complex_insights.get('complex_modules', [])
        
        summary_parts.append(f"## Complexity Analysis\n\n")
        summary_parts.append(f"The codebase has an average complexity of **{avg_complexity:.2f}**. ")
        
        if complex_files:
            summary_parts.append(f"There are **{len(complex_files)}** complex files, ")
            summary_parts.append(f"with the most complex being **{complex_files[0]['path']}** ")
            summary_parts.append(f"(complexity score: {complex_files[0]['complexity']:.2f}).\n\n")
        else:
            summary_parts.append(f"No notably complex files were found.\n\n")
        
        if complex_modules:
            summary_parts.append(f"The most complex module is **{complex_modules[0]['module']}** ")
            summary_parts.append(f"with an average complexity of {complex_modules[0]['average_complexity']:.2f}.\n\n")
        
        # Dependency insights
        dep_insights = self.insights.get('dependencies', {})
        circular_deps = dep_insights.get('circular_dependencies', [])
        connected_modules = dep_insights.get('highly_connected_modules', [])
        bottlenecks = dep_insights.get('bottlenecks', [])
        
        summary_parts.append(f"## Dependency Analysis\n\n")
        
        if circular_deps:
            summary_parts.append(f"**{len(circular_deps)}** circular dependencies were detected. ")
            summary_parts.append(f"This may indicate architectural issues that should be addressed.\n\n")
        else:
            summary_parts.append(f"No circular dependencies were detected, which is a positive sign.\n\n")
        
        if connected_modules:
            summary_parts.append(f"The most connected module is **{connected_modules[0]['module']}** ")
            summary_parts.append(f"with {connected_modules[0]['total']} total connections ")
            summary_parts.append(f"({connected_modules[0]['incoming']} incoming, {connected_modules[0]['outgoing']} outgoing).\n\n")
        
        if bottlenecks:
            summary_parts.append(f"Potential bottleneck modules include **{bottlenecks[0]['module']}** ")
            summary_parts.append(f"({bottlenecks[0]['incoming']} incoming dependencies).\n\n")
        
        # Hotspots
        hotspot_insights = self.insights.get('hotspots', {})
        complex_hotspots = hotspot_insights.get('complex_hotspots', [])
        
        if complex_hotspots:
            summary_parts.append(f"## Code Hotspots\n\n")
            summary_parts.append(f"Key areas that may require attention due to high complexity and dependencies:\n\n")
            
            for hotspot in complex_hotspots[:3]:
                summary_parts.append(f"- **{hotspot['file']}** (complexity: {hotspot['complexity']:.2f}, ")
                summary_parts.append(f"module dependencies: {hotspot['module_dependencies']})\n")
            
            summary_parts.append("\n")
        
        # Recommendations
        recommendations = arch_insights.get('recommendations', [])
        
        if recommendations:
            summary_parts.append(f"## Recommendations\n\n")
            
            for i, rec in enumerate(recommendations):
                summary_parts.append(f"{i+1}. {rec}\n")
            
            summary_parts.append("\n")
        
        return "".join(summary_parts)

    def get_top_insights(self) -> Dict[str, Any]:
        """
        Get the top insights in a simplified format.

        Returns:
            Dictionary of simplified top insights
        """
        # Ensure insights are generated
        if not self.insights:
            self.generate_insights()
        
        top_insights = {
            'architecture_type': self.insights.get('architecture', {}).get('architecture_type', 'Unknown'),
            'modularity_score': self.insights.get('architecture', {}).get('modularity_score', 0),
            'primary_language': self.insights.get('language', {}).get('primary_language', 'Unknown'),
            'average_complexity': self.insights.get('complexity', {}).get('average_complexity', 0),
            'circular_dependencies_count': len(self.insights.get('dependencies', {}).get('circular_dependencies', [])),
            'complex_files_count': len(self.insights.get('complexity', {}).get('complex_files', [])),
            'top_hotspots': [h['file'] for h in self.insights.get('hotspots', {}).get('complex_hotspots', [])[:3]],
            'recommendations': self.insights.get('architecture', {}).get('recommendations', [])
        }
        
        return top_insights 