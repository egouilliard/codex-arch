"""
Report Module

This module provides functionality for generating reports about code architecture,
including dependency diagrams, metrics, and complexity analysis.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union
import datetime

from codex_arch.storage import get_storage

logger = logging.getLogger(__name__)

def generate_report(
    repo_path: str,
    output_dir: Optional[str] = None,
    report_type: str = "full",
    include_metrics: bool = True,
    include_dependencies: bool = True,
    include_complexity: bool = True,
    format: str = "html",
) -> Dict[str, Any]:
    """
    Generate a report about code architecture.
    
    Args:
        repo_path: Path to the repository to report on
        output_dir: Directory to store report output
        report_type: Type of report (full, summary, metrics, dependencies, complexity)
        include_metrics: Whether to include metrics in the report
        include_dependencies: Whether to include dependencies in the report
        include_complexity: Whether to include complexity analysis in the report
        format: Output format (html, markdown, json)
        
    Returns:
        Dictionary containing report metadata
    """
    logger.info(f"Generating {report_type} report for {repo_path}")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
    
    # Get stored analysis data
    storage = get_storage()
    analysis_data = storage.get_analysis_data()
    
    # If no analysis data, return error
    if not analysis_data:
        logger.error("No analysis data found for reporting")
        return {
            "error": "No analysis data found",
            "status": "error",
        }
    
    # Initialize report metadata
    report_metadata = {
        "repository": repo_path,
        "report_type": report_type,
        "report_date": datetime.datetime.now().isoformat(),
        "included_sections": [],
        "output_format": format,
        "output_path": "",
    }
    
    # Generate report content based on type
    report_content = {}
    
    if report_type == "full" or report_type == "summary":
        # Repository info
        report_content["repository_info"] = {
            "path": repo_path,
            "name": os.path.basename(repo_path),
            "last_analyzed": storage.get_last_analyzed_commit(),
        }
        report_metadata["included_sections"].append("repository_info")
    
    if (report_type == "full" or report_type == "metrics") and include_metrics:
        # Metrics
        metrics = {}
        
        # Get metrics from analysis data
        for path, path_metrics in analysis_data.get("file_metrics", {}).items():
            metrics.update(path_metrics)
        
        # Summary metrics
        summary_metrics = {
            "total_files": metrics.get("file_counts", {}).get("total", 0),
            "total_lines": metrics.get("line_counts", {}).get("total", 0),
            "average_lines_per_file": metrics.get("line_counts", {}).get("average_per_file", 0),
            "language_breakdown": metrics.get("language_analysis", {}).get("by_language", {}),
            "top_languages": metrics.get("language_analysis", {}).get("top_languages", []),
        }
        
        report_content["metrics"] = summary_metrics
        report_metadata["included_sections"].append("metrics")
    
    if (report_type == "full" or report_type == "dependencies") and include_dependencies:
        # Dependencies
        dependency_graph = analysis_data.get("dependency_graph", {})
        
        # Convert to format suitable for reporting
        dependency_report = {
            "total_dependencies": sum(len(deps) for deps in dependency_graph.values()),
            "total_files_with_dependencies": len(dependency_graph),
            "dependency_graph": dependency_graph,
        }
        
        report_content["dependencies"] = dependency_report
        report_metadata["included_sections"].append("dependencies")
    
    if (report_type == "full" or report_type == "complexity") and include_complexity:
        # Complexity
        complexity_metrics = {}
        
        # Get complexity metrics from analysis data
        for path, path_metrics in analysis_data.get("file_metrics", {}).items():
            if "complexity_metrics" in path_metrics:
                complexity_metrics.update(path_metrics["complexity_metrics"])
        
        report_content["complexity"] = complexity_metrics
        report_metadata["included_sections"].append("complexity")
    
    # Generate report file
    if format == "json":
        output_path = os.path.join(output_dir, "architecture_report.json")
        with open(output_path, "w") as f:
            json.dump(report_content, f, indent=2)
        report_metadata["output_path"] = output_path
    
    elif format == "markdown":
        output_path = os.path.join(output_dir, "architecture_report.md")
        with open(output_path, "w") as f:
            # Write markdown header
            f.write(f"# Code Architecture Report: {os.path.basename(repo_path)}\n\n")
            f.write(f"**Generated:** {report_metadata['report_date']}\n\n")
            
            # Write each section
            if "repository_info" in report_content:
                f.write("## Repository Information\n\n")
                repo_info = report_content["repository_info"]
                f.write(f"- **Repository:** {repo_info['name']}\n")
                f.write(f"- **Path:** {repo_info['path']}\n")
                f.write(f"- **Last Analyzed Commit:** {repo_info['last_analyzed']}\n\n")
            
            if "metrics" in report_content:
                f.write("## Code Metrics\n\n")
                metrics = report_content["metrics"]
                f.write(f"- **Total Files:** {metrics['total_files']}\n")
                f.write(f"- **Total Lines:** {metrics['total_lines']}\n")
                f.write(f"- **Average Lines per File:** {metrics['average_lines_per_file']}\n\n")
                
                if metrics.get("top_languages"):
                    f.write("### Top Languages\n\n")
                    for lang in metrics["top_languages"]:
                        f.write(f"- **{lang['name']}:** {lang['percentage']}% ({lang['lines']} lines)\n")
            
            if "dependencies" in report_content:
                f.write("\n## Dependencies\n\n")
                deps = report_content["dependencies"]
                f.write(f"- **Total Dependencies:** {deps['total_dependencies']}\n")
                f.write(f"- **Files with Dependencies:** {deps['total_files_with_dependencies']}\n\n")
            
            if "complexity" in report_content:
                f.write("\n## Code Complexity\n\n")
                complexity = report_content["complexity"]
                if "average_complexity" in complexity:
                    f.write(f"- **Average Complexity:** {complexity['average_complexity']}\n")
                if "most_complex_files" in complexity and complexity["most_complex_files"]:
                    f.write("\n### Most Complex Files\n\n")
                    for i, file_info in enumerate(complexity["most_complex_files"][:5], 1):
                        f.write(f"{i}. **{file_info['path']}** - Complexity: {file_info['complexity']}")
                        if "lines" in file_info:
                            f.write(f" - Lines: {file_info['lines']}")
                        f.write("\n")
        
        report_metadata["output_path"] = output_path
    
    else:  # HTML format
        output_path = os.path.join(output_dir, "architecture_report.html")
        with open(output_path, "w") as f:
            # Write HTML header
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n<head>\n")
            f.write(f"<title>Code Architecture Report: {os.path.basename(repo_path)}</title>\n")
            f.write("<style>\n")
            f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
            f.write("h1 { color: #333; }\n")
            f.write("h2 { color: #555; margin-top: 30px; }\n")
            f.write("h3 { color: #777; }\n")
            f.write("table { border-collapse: collapse; width: 100%; }\n")
            f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
            f.write("th { background-color: #f2f2f2; }\n")
            f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
            f.write("</style>\n")
            f.write("</head>\n<body>\n")
            
            # Report header
            f.write(f"<h1>Code Architecture Report: {os.path.basename(repo_path)}</h1>\n")
            f.write(f"<p><strong>Generated:</strong> {report_metadata['report_date']}</p>\n")
            
            # Write each section
            if "repository_info" in report_content:
                f.write("<h2>Repository Information</h2>\n")
                repo_info = report_content["repository_info"]
                f.write("<ul>\n")
                f.write(f"<li><strong>Repository:</strong> {repo_info['name']}</li>\n")
                f.write(f"<li><strong>Path:</strong> {repo_info['path']}</li>\n")
                f.write(f"<li><strong>Last Analyzed Commit:</strong> {repo_info['last_analyzed']}</li>\n")
                f.write("</ul>\n")
            
            if "metrics" in report_content:
                f.write("<h2>Code Metrics</h2>\n")
                metrics = report_content["metrics"]
                f.write("<ul>\n")
                f.write(f"<li><strong>Total Files:</strong> {metrics['total_files']}</li>\n")
                f.write(f"<li><strong>Total Lines:</strong> {metrics['total_lines']}</li>\n")
                f.write(f"<li><strong>Average Lines per File:</strong> {metrics['average_lines_per_file']}</li>\n")
                f.write("</ul>\n")
                
                if metrics.get("top_languages"):
                    f.write("<h3>Top Languages</h3>\n")
                    f.write("<table>\n")
                    f.write("<tr><th>Language</th><th>Percentage</th><th>Lines</th></tr>\n")
                    for lang in metrics["top_languages"]:
                        f.write(f"<tr><td>{lang['name']}</td><td>{lang['percentage']}%</td><td>{lang['lines']}</td></tr>\n")
                    f.write("</table>\n")
            
            if "dependencies" in report_content:
                f.write("<h2>Dependencies</h2>\n")
                deps = report_content["dependencies"]
                f.write("<ul>\n")
                f.write(f"<li><strong>Total Dependencies:</strong> {deps['total_dependencies']}</li>\n")
                f.write(f"<li><strong>Files with Dependencies:</strong> {deps['total_files_with_dependencies']}</li>\n")
                f.write("</ul>\n")
            
            if "complexity" in report_content:
                f.write("<h2>Code Complexity</h2>\n")
                complexity = report_content["complexity"]
                f.write("<ul>\n")
                if "average_complexity" in complexity:
                    f.write(f"<li><strong>Average Complexity:</strong> {complexity['average_complexity']}</li>\n")
                f.write("</ul>\n")
                
                if "most_complex_files" in complexity and complexity["most_complex_files"]:
                    f.write("<h3>Most Complex Files</h3>\n")
                    f.write("<table>\n")
                    f.write("<tr><th>#</th><th>File</th><th>Complexity</th><th>Lines</th></tr>\n")
                    for i, file_info in enumerate(complexity["most_complex_files"][:5], 1):
                        f.write(f"<tr><td>{i}</td><td>{file_info['path']}</td><td>{file_info['complexity']}</td>")
                        if "lines" in file_info:
                            f.write(f"<td>{file_info['lines']}</td>")
                        else:
                            f.write("<td>-</td>")
                        f.write("</tr>\n")
                    f.write("</table>\n")
            
            # HTML footer
            f.write("</body>\n</html>")
        
        report_metadata["output_path"] = output_path
    
    logger.info(f"Report generated and saved to {output_path}")
    
    return report_metadata 