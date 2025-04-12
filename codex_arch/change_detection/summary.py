"""
Change Summary Generation Module

This module provides functionality to generate summaries of detected changes,
highlighting modifications to the codebase structure and dependencies.
"""

import os
import logging
import json
from typing import Dict, List, Set, Any, Optional, Tuple
from datetime import datetime

from codex_arch.change_detection.git_changes import GitChangeDetector

logger = logging.getLogger(__name__)

class ChangeSummaryGenerator:
    """
    Generates summaries of repository changes.
    
    This class provides methods to create human-readable summaries of changes
    detected between git commits, highlighting impacts on the codebase structure.
    """
    
    def __init__(self, repo_path: str = '.'):
        """
        Initialize the ChangeSummaryGenerator.
        
        Args:
            repo_path: Path to the git repository. Defaults to current directory.
        """
        self.repo_path = repo_path
        self.git_detector = GitChangeDetector(repo_path)
    
    def generate_change_summary(self, 
                               from_commit: str = 'HEAD~1', 
                               to_commit: str = 'HEAD',
                               dependency_analysis: Optional[Dict[str, Any]] = None,
                               metrics_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of changes between commits.
        
        Args:
            from_commit: The base commit to compare from. Defaults to the previous commit.
            to_commit: The target commit to compare to. Defaults to the current HEAD.
            dependency_analysis: Optional dependency analysis results for affected modules.
            metrics_analysis: Optional metrics analysis results for further insights.
            
        Returns:
            Dictionary containing the change summary.
        """
        logger.info(f"Generating change summary from {from_commit} to {to_commit}")
        
        # Get basic change information
        changes = self.git_detector.get_changes(from_commit, to_commit)
        all_changed_files = set().union(*changes.values())
        
        # Get commit info
        from_commit_info = self.git_detector.get_commit_info(from_commit)
        to_commit_info = self.git_detector.get_commit_info(to_commit)
        
        # Build basic summary
        summary = {
            'from_commit': from_commit_info,
            'to_commit': to_commit_info,
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'added_files': len(changes.get('added', set())),
                'modified_files': len(changes.get('modified', set())),
                'deleted_files': len(changes.get('deleted', set())),
                'total_changes': len(all_changed_files)
            },
            'file_changes': {
                'added': sorted(list(changes.get('added', set()))),
                'modified': sorted(list(changes.get('modified', set()))),
                'deleted': sorted(list(changes.get('deleted', set())))
            }
        }
        
        # Add language-specific stats
        summary['language_stats'] = self._get_language_stats(all_changed_files)
        
        # Add affected modules information if we have dependency analysis
        if dependency_analysis:
            affected_modules = self._analyze_affected_modules(changes, dependency_analysis)
            summary['affected_modules'] = affected_modules
        
        # Add metrics impact if we have metrics analysis
        if metrics_analysis:
            metrics_impact = self._analyze_metrics_impact(changes, metrics_analysis)
            summary['metrics_impact'] = metrics_impact
        
        return summary
    
    def generate_markdown_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate a markdown representation of the change summary.
        
        Args:
            summary: Change summary dictionary as returned by generate_change_summary.
            
        Returns:
            Markdown formatted string of the change summary.
        """
        md = []
        
        # Summary header
        md.append("# Change Summary\n")
        
        # Commits information
        md.append("## Commits\n")
        md.append(f"**From:** {summary['from_commit']['hash'][:8]} - {summary['from_commit']['message'][:50]}...")
        md.append(f" (by {summary['from_commit']['author']} on {summary['from_commit']['date'][:10]})\n")
        
        md.append(f"**To:** {summary['to_commit']['hash'][:8]} - {summary['to_commit']['message'][:50]}...")
        md.append(f" (by {summary['to_commit']['author']} on {summary['to_commit']['date'][:10]})\n")
        
        # Change stats
        md.append("## Change Statistics\n")
        stats = summary['stats']
        md.append(f"- **Added Files:** {stats['added_files']}")
        md.append(f"- **Modified Files:** {stats['modified_files']}")
        md.append(f"- **Deleted Files:** {stats['deleted_files']}")
        md.append(f"- **Total Changes:** {stats['total_changes']}\n")
        
        # Language stats if available
        if 'language_stats' in summary:
            md.append("### Language Breakdown\n")
            md.append("| Language | Files Changed |")
            md.append("|----------|---------------|")
            for lang, count in summary['language_stats'].items():
                md.append(f"| {lang} | {count} |")
            md.append("")
        
        # File changes
        self._add_file_section(md, "Added Files", summary['file_changes']['added'])
        self._add_file_section(md, "Modified Files", summary['file_changes']['modified'])
        self._add_file_section(md, "Deleted Files", summary['file_changes']['deleted'])
        
        # Affected modules
        if 'affected_modules' in summary:
            md.append("## Affected Modules\n")
            
            if summary['affected_modules']['direct']:
                md.append("### Directly Modified Modules\n")
                for module in summary['affected_modules']['direct']:
                    md.append(f"- **{module}**")
                md.append("")
            
            if summary['affected_modules']['indirect']:
                md.append("### Indirectly Affected Modules (Dependency Impact)\n")
                for module, impacting in summary['affected_modules']['indirect'].items():
                    md.append(f"- **{module}** - Affected by changes in: {', '.join(impacting)}")
                md.append("")
            
            if 'dependency_changes' in summary['affected_modules']:
                md.append("### Dependency Changes\n")
                for change in summary['affected_modules']['dependency_changes']:
                    md.append(f"- {change}")
                md.append("")
        
        # Metrics impact
        if 'metrics_impact' in summary:
            md.append("## Metrics Impact\n")
            metrics = summary['metrics_impact']
            
            if 'complexity_changes' in metrics:
                md.append("### Complexity Changes\n")
                md.append("| Metric | Before | After | Change |")
                md.append("|--------|--------|-------|--------|")
                for metric, values in metrics['complexity_changes'].items():
                    change = values['after'] - values['before']
                    change_str = f"+{change}" if change > 0 else str(change)
                    md.append(f"| {metric} | {values['before']} | {values['after']} | {change_str} |")
                md.append("")
            
            if 'significant_changes' in metrics:
                md.append("### Significant Changes\n")
                for change in metrics['significant_changes']:
                    md.append(f"- {change}")
                md.append("")
        
        return "\n".join(md)
    
    def _add_file_section(self, md_lines: List[str], title: str, files: List[str]) -> None:
        """
        Add a section for a file change type to the markdown summary.
        
        Args:
            md_lines: List of markdown lines to append to.
            title: Section title.
            files: List of files to include.
        """
        if not files:
            return
            
        md_lines.append(f"### {title}\n")
        
        # Group files by directory for better organization
        grouped_files = {}
        for file in files:
            dir_name = os.path.dirname(file)
            if not dir_name:
                dir_name = "/"
            
            if dir_name not in grouped_files:
                grouped_files[dir_name] = []
            
            grouped_files[dir_name].append(os.path.basename(file))
        
        # Add each directory group
        for dir_name, dir_files in sorted(grouped_files.items()):
            if dir_name == "/":
                dir_display = "(root)"
            else:
                dir_display = dir_name
                
            md_lines.append(f"**{dir_display}/**")
            for file in sorted(dir_files):
                md_lines.append(f"- {file}")
            md_lines.append("")
    
    def _get_language_stats(self, changed_files: Set[str]) -> Dict[str, int]:
        """
        Get statistics on changed files by language/extension.
        
        Args:
            changed_files: Set of changed file paths.
            
        Returns:
            Dictionary mapping file extension/language to count.
        """
        extension_count = {}
        
        for file_path in changed_files:
            ext = os.path.splitext(file_path)[1]
            if not ext:
                ext = "No Extension"
            else:
                # Remove the dot and convert to language name
                ext = ext[1:].upper()
                
                # Use more human-readable names for common extensions
                ext_map = {
                    "PY": "Python",
                    "JS": "JavaScript",
                    "TS": "TypeScript",
                    "JSX": "React JSX",
                    "TSX": "React TSX",
                    "HTML": "HTML",
                    "CSS": "CSS",
                    "MD": "Markdown",
                    "YML": "YAML",
                    "YAML": "YAML",
                    "JSON": "JSON",
                    "TXT": "Text"
                }
                
                ext = ext_map.get(ext, ext)
            
            extension_count[ext] = extension_count.get(ext, 0) + 1
        
        # Sort by count descending
        return dict(sorted(extension_count.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_affected_modules(self, 
                                 changes: Dict[str, Set[str]],
                                 dependency_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze which modules are affected by the changes.
        
        Args:
            changes: Dictionary containing sets of added, modified, and deleted files.
            dependency_analysis: Dependency analysis results.
            
        Returns:
            Dictionary with affected modules information.
        """
        # Get directly modified modules
        affected_modules = self.git_detector.get_affected_modules(changes, file_extensions=['.py'])
        
        # Convert file paths to module names
        direct_modules = set()
        for module in affected_modules:
            module_name = self._file_path_to_module_name(module)
            direct_modules.add(module_name)
        
        # Find indirectly affected modules (those depending on changed modules)
        indirect_modules = {}
        deps = dependency_analysis.get('dependencies', {})
        
        for module, dependencies in deps.items():
            # Skip if this module was directly modified
            if module in direct_modules:
                continue
                
            # Check if any of its dependencies were modified
            impacting_modules = []
            for dep in dependencies:
                if dep in direct_modules:
                    impacting_modules.append(dep)
            
            if impacting_modules:
                indirect_modules[module] = impacting_modules
        
        # Identify specific dependency changes
        dependency_changes = []
        
        # New modules
        for file_path in changes.get('added', set()):
            if file_path.endswith('.py'):
                module_name = self._file_path_to_module_name(file_path)
                if module_name in deps:
                    dependent_count = sum(1 for m, d in deps.items() if module_name in d)
                    dependency_changes.append(f"New module '{module_name}' created (used by {dependent_count} modules)")
        
        # Deleted modules
        for file_path in changes.get('deleted', set()):
            if file_path.endswith('.py'):
                module_name = self._file_path_to_module_name(file_path)
                dependency_changes.append(f"Module '{module_name}' deleted")
        
        return {
            'direct': sorted(list(direct_modules)),
            'indirect': indirect_modules,
            'dependency_changes': dependency_changes
        }
    
    def _file_path_to_module_name(self, file_path: str) -> str:
        """
        Convert a file path to a Python module name.
        
        Args:
            file_path: Path to the Python file.
            
        Returns:
            Python module name.
        """
        if not file_path.endswith('.py'):
            return file_path
            
        # Remove .py extension
        module_path = file_path[:-3]
        # Replace directory separators with dots
        module_name = module_path.replace('/', '.').replace('\\', '.')
        # Remove __init__ from the end if present
        if module_name.endswith('.__init__'):
            module_name = module_name[:-9]
            
        return module_name
    
    def _analyze_metrics_impact(self, 
                               changes: Dict[str, Set[str]],
                               metrics_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of changes on code metrics.
        
        Args:
            changes: Dictionary containing sets of added, modified, and deleted files.
            metrics_analysis: Metrics analysis results.
            
        Returns:
            Dictionary with metrics impact information.
        """
        # Get basic stats
        total_files = metrics_analysis.get('aggregated', {}).get('total_files', 0)
        total_loc = metrics_analysis.get('aggregated', {}).get('total_loc', 0)
        
        # Check for significant changes in complexity or size
        significant_changes = []
        
        # Significant size changes
        added_files = len(changes.get('added', set()))
        if added_files > 10 or added_files > total_files * 0.1:
            significant_changes.append(f"Added {added_files} new files ({(added_files/total_files*100):.1f}% increase)")
        
        deleted_files = len(changes.get('deleted', set()))
        if deleted_files > 10 or deleted_files > total_files * 0.1:
            significant_changes.append(f"Removed {deleted_files} files ({(deleted_files/total_files*100):.1f}% decrease)")
        
        # Complexity changes (comparing current with previous)
        complexity_changes = {
            'Total Files': {
                'before': total_files - added_files + deleted_files,
                'after': total_files
            },
            'Total Lines of Code': {
                'before': 0,  # Would need historical data
                'after': total_loc
            }
        }
        
        # TODO: Add more detailed complexity metrics if we had historical data
        
        return {
            'complexity_changes': complexity_changes,
            'significant_changes': significant_changes
        }
        
    def save_summary_to_file(self, 
                            summary: Dict[str, Any], 
                            output_path: str = 'change_summary.md') -> bool:
        """
        Save the change summary to a file.
        
        Args:
            summary: Change summary dictionary.
            output_path: Path to save the summary file. Defaults to 'change_summary.md'.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            markdown = self.generate_markdown_summary(summary)
            
            with open(output_path, 'w') as f:
                f.write(markdown)
                
            logger.info(f"Change summary saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving change summary: {str(e)}")
            return False 