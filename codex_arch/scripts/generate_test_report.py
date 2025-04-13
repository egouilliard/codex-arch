#!/usr/bin/env python3
"""
Test Report Generator for Codex-Arch

This script generates consolidated HTML reports from test results.
It combines JUnit XML reports, coverage data, and test outputs.
"""

import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


class TestReportGenerator:
    """Generates consolidated test reports from various test outputs."""

    def __init__(self, output_dir, input_dir=None, project_name="Codex-Arch"):
        """
        Initialize the report generator.
        
        Args:
            output_dir (str): Directory to write the report to
            input_dir (str, optional): Directory containing test outputs (defaults to tests/output/latest)
            project_name (str, optional): Name of the project
        """
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        
        # Set up input directory
        if input_dir:
            self.input_dir = Path(input_dir)
        else:
            # Find the most recent test output directory
            output_dirs = sorted(glob.glob("tests/output/*"), reverse=True)
            if not output_dirs:
                print("Error: No test output directories found.")
                sys.exit(1)
            self.input_dir = Path(output_dirs[0])
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Data structures to hold test information
        self.test_results = {
            "unit": {"passed": 0, "failed": 0, "skipped": 0, "error": 0, "total": 0, "time": 0},
            "integration": {"passed": 0, "failed": 0, "skipped": 0, "error": 0, "total": 0, "time": 0},
            "e2e": {"passed": 0, "failed": 0, "skipped": 0, "error": 0, "total": 0, "time": 0},
        }
        
        self.failed_tests = []
        self.coverage_data = {
            "percent": 0,
            "covered_lines": 0,
            "total_lines": 0,
            "modules": [],
        }
        
        print(f"Input directory: {self.input_dir}")
        print(f"Output directory: {self.output_dir}")

    def parse_junit_xml(self):
        """Parse JUnit XML files and extract test results."""
        junit_files = list(self.input_dir.glob("**/junit*.xml")) + list(self.input_dir.glob("**/TEST-*.xml"))
        
        if not junit_files:
            print("Warning: No JUnit XML files found.")
            return
        
        for junit_file in junit_files:
            try:
                tree = ET.parse(junit_file)
                root = tree.getroot()
                
                # Determine test type based on filename or content
                test_type = "unit"  # Default
                file_path = str(junit_file)
                if "integration" in file_path:
                    test_type = "integration"
                elif "e2e" in file_path:
                    test_type = "e2e"
                
                # Parse testsuite elements
                for testsuite in root.findall(".//testsuite"):
                    self.test_results[test_type]["total"] += int(testsuite.get("tests", 0))
                    self.test_results[test_type]["passed"] += int(testsuite.get("tests", 0)) - int(testsuite.get("failures", 0)) - int(testsuite.get("errors", 0)) - int(testsuite.get("skipped", 0))
                    self.test_results[test_type]["failed"] += int(testsuite.get("failures", 0))
                    self.test_results[test_type]["error"] += int(testsuite.get("errors", 0))
                    self.test_results[test_type]["skipped"] += int(testsuite.get("skipped", 0))
                    self.test_results[test_type]["time"] += float(testsuite.get("time", 0))
                    
                    # Collect failed tests
                    for testcase in testsuite.findall(".//testcase"):
                        failure = testcase.find("failure")
                        error = testcase.find("error")
                        
                        if failure is not None or error is not None:
                            classname = testcase.get("classname", "")
                            name = testcase.get("name", "")
                            message = ""
                            
                            if failure is not None:
                                message = failure.get("message", "")
                            elif error is not None:
                                message = error.get("message", "")
                            
                            self.failed_tests.append({
                                "type": test_type,
                                "classname": classname,
                                "name": name,
                                "message": message
                            })
            
            except Exception as e:
                print(f"Error parsing JUnit XML file {junit_file}: {e}")

    def parse_coverage_data(self):
        """Parse coverage data from coverage XML file."""
        coverage_file = self.input_dir / "coverage.xml"
        
        if not coverage_file.exists():
            print("Warning: No coverage.xml file found.")
            return
        
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            # Get overall coverage
            coverage = root.get("line-rate", "0")
            self.coverage_data["percent"] = float(coverage) * 100
            
            # Get total lines
            lines_covered = int(root.get("lines-covered", "0"))
            lines_valid = int(root.get("lines-valid", "0"))
            self.coverage_data["covered_lines"] = lines_covered
            self.coverage_data["total_lines"] = lines_valid
            
            # Get module-specific coverage
            for package in root.findall(".//package"):
                for cls in package.findall(".//class"):
                    filename = cls.get("filename", "")
                    line_rate = float(cls.get("line-rate", "0")) * 100
                    
                    self.coverage_data["modules"].append({
                        "name": filename,
                        "coverage": line_rate
                    })
            
            # Sort modules by coverage (lowest first)
            self.coverage_data["modules"].sort(key=lambda x: x["coverage"])
        
        except Exception as e:
            print(f"Error parsing coverage data: {e}")

    def generate_html_report(self):
        """Generate HTML report from the collected data."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate total results
        total_results = {
            "passed": sum(data["passed"] for data in self.test_results.values()),
            "failed": sum(data["failed"] for data in self.test_results.values()),
            "skipped": sum(data["skipped"] for data in self.test_results.values()),
            "error": sum(data["error"] for data in self.test_results.values()),
            "total": sum(data["total"] for data in self.test_results.values()),
            "time": sum(data["time"] for data in self.test_results.values()),
        }
        
        # Create HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project_name} - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background-color: #4a5568; color: white; padding: 20px; margin-bottom: 20px; text-align: center; }}
        h1, h2, h3 {{ margin-top: 0; }}
        .summary {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px; }}
        .card {{ flex: 1; min-width: 250px; background-color: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; }}
        .card h3 {{ margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        .stats {{ display: flex; justify-content: space-between; margin-top: 15px; }}
        .stat {{ text-align: center; flex: 1; }}
        .stat-value {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
        .stat-label {{ font-size: 12px; color: #666; }}
        .passed {{ color: #38a169; }}
        .failed {{ color: #e53e3e; }}
        .skipped {{ color: #d69e2e; }}
        .error {{ color: #9f1239; }}
        .progress {{ height: 20px; background-color: #edf2f7; border-radius: 10px; overflow: hidden; margin: 20px 0; }}
        .progress-bar {{ height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 0.5s; }}
        .progress-bar.good {{ background-color: #38a169; }}
        .progress-bar.warning {{ background-color: #d69e2e; }}
        .progress-bar.danger {{ background-color: #e53e3e; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4a5568; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; color: white; margin-right: 5px; }}
        .badge.unit {{ background-color: #4299e1; }}
        .badge.integration {{ background-color: #805ad5; }}
        .badge.e2e {{ background-color: #dd6b20; }}
        footer {{ margin-top: 40px; text-align: center; font-size: 14px; color: #666; border-top: 1px solid #eee; padding-top: 20px; }}
    </style>
</head>
<body>
    <header>
        <h1>{self.project_name}</h1>
        <p>Test Report generated on {timestamp}</p>
    </header>
    <div class="container">
        <div class="summary">
            <div class="card">
                <h3>Test Summary</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{total_results['total']}</div>
                        <div class="stat-label">TOTAL</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value passed">{total_results['passed']}</div>
                        <div class="stat-label">PASSED</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value failed">{total_results['failed']}</div>
                        <div class="stat-label">FAILED</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value skipped">{total_results['skipped']}</div>
                        <div class="stat-label">SKIPPED</div>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar {'good' if total_results['passed'] == total_results['total'] else 'warning' if total_results['failed'] / total_results['total'] < 0.2 else 'danger'}" style="width: {100 * total_results['passed'] / total_results['total'] if total_results['total'] > 0 else 0}%">
                        {f"{100 * total_results['passed'] / total_results['total']:.1f}%" if total_results['total'] > 0 else '0%'}
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Code Coverage</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{self.coverage_data['total_lines']}</div>
                        <div class="stat-label">TOTAL LINES</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{self.coverage_data['covered_lines']}</div>
                        <div class="stat-label">COVERED LINES</div>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar {'good' if self.coverage_data['percent'] >= 80 else 'warning' if self.coverage_data['percent'] >= 60 else 'danger'}" style="width: {self.coverage_data['percent']}%">
                        {f"{self.coverage_data['percent']:.1f}%"}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <div class="card">
                <h3>Unit Tests</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{self.test_results['unit']['total']}</div>
                        <div class="stat-label">TOTAL</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value passed">{self.test_results['unit']['passed']}</div>
                        <div class="stat-label">PASSED</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value failed">{self.test_results['unit']['failed'] + self.test_results['unit']['error']}</div>
                        <div class="stat-label">FAILED</div>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar {'good' if self.test_results['unit']['passed'] == self.test_results['unit']['total'] else 'warning' if self.test_results['unit']['failed'] / self.test_results['unit']['total'] < 0.2 else 'danger'}" style="width: {100 * self.test_results['unit']['passed'] / self.test_results['unit']['total'] if self.test_results['unit']['total'] > 0 else 0}%">
                        {f"{100 * self.test_results['unit']['passed'] / self.test_results['unit']['total']:.1f}%" if self.test_results['unit']['total'] > 0 else '0%'}
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Integration Tests</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{self.test_results['integration']['total']}</div>
                        <div class="stat-label">TOTAL</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value passed">{self.test_results['integration']['passed']}</div>
                        <div class="stat-label">PASSED</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value failed">{self.test_results['integration']['failed'] + self.test_results['integration']['error']}</div>
                        <div class="stat-label">FAILED</div>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar {'good' if self.test_results['integration']['passed'] == self.test_results['integration']['total'] else 'warning' if self.test_results['integration']['failed'] / self.test_results['integration']['total'] < 0.2 else 'danger'}" style="width: {100 * self.test_results['integration']['passed'] / self.test_results['integration']['total'] if self.test_results['integration']['total'] > 0 else 0}%">
                        {f"{100 * self.test_results['integration']['passed'] / self.test_results['integration']['total']:.1f}%" if self.test_results['integration']['total'] > 0 else '0%'}
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>End-to-End Tests</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{self.test_results['e2e']['total']}</div>
                        <div class="stat-label">TOTAL</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value passed">{self.test_results['e2e']['passed']}</div>
                        <div class="stat-label">PASSED</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value failed">{self.test_results['e2e']['failed'] + self.test_results['e2e']['error']}</div>
                        <div class="stat-label">FAILED</div>
                    </div>
                </div>
                <div class="progress">
                    <div class="progress-bar {'good' if self.test_results['e2e']['passed'] == self.test_results['e2e']['total'] else 'warning' if self.test_results['e2e']['failed'] / self.test_results['e2e']['total'] < 0.2 else 'danger'}" style="width: {100 * self.test_results['e2e']['passed'] / self.test_results['e2e']['total'] if self.test_results['e2e']['total'] > 0 else 0}%">
                        {f"{100 * self.test_results['e2e']['passed'] / self.test_results['e2e']['total']:.1f}%" if self.test_results['e2e']['total'] > 0 else '0%'}
                    </div>
                </div>
            </div>
        </div>
        
        <h2>Failed Tests</h2>
        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Test</th>
                    <th>Error Message</th>
                </tr>
            </thead>
            <tbody>
"""
        if self.failed_tests:
            for test in self.failed_tests:
                html += f"""
                <tr>
                    <td><span class="badge {test['type']}">{test['type'].upper()}</span></td>
                    <td>{test['classname']}.{test['name']}</td>
                    <td>{test['message']}</td>
                </tr>
"""
        else:
            html += """
                <tr>
                    <td colspan="3" style="text-align: center;">No failed tests! 🎉</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>Coverage Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Module</th>
                    <th>Coverage</th>
                </tr>
            </thead>
            <tbody>
"""
        
        if self.coverage_data["modules"]:
            for module in self.coverage_data["modules"]:
                coverage_class = "good" if module["coverage"] >= 80 else "warning" if module["coverage"] >= 60 else "danger"
                html += f"""
                <tr>
                    <td>{module['name']}</td>
                    <td>
                        <div class="progress" style="margin: 0;">
                            <div class="progress-bar {coverage_class}" style="width: {module['coverage']}%">
                                {module['coverage']:.1f}%
                            </div>
                        </div>
                    </td>
                </tr>
"""
        else:
            html += """
                <tr>
                    <td colspan="2" style="text-align: center;">No coverage data available</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <footer>
            <p>Generated by Codex-Arch Test Report Generator</p>
        </footer>
    </div>
</body>
</html>
"""
        
        # Write HTML to file
        report_file = self.output_dir / "test_report.html"
        with open(report_file, "w") as f:
            f.write(html)
        
        print(f"HTML report generated: {report_file}")
        return report_file
    
    def generate_json_report(self):
        """Generate JSON report from the collected data."""
        report_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project": self.project_name,
            "test_results": self.test_results,
            "failed_tests": self.failed_tests,
            "coverage": self.coverage_data,
        }
        
        # Write JSON to file
        json_file = self.output_dir / "test_report.json"
        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"JSON report generated: {json_file}")
        return json_file
    
    def generate_reports(self):
        """Parse test data and generate all reports."""
        self.parse_junit_xml()
        self.parse_coverage_data()
        html_report = self.generate_html_report()
        json_report = self.generate_json_report()
        
        return {
            "html": str(html_report),
            "json": str(json_report)
        }


def main():
    """Main function to parse arguments and generate reports."""
    parser = argparse.ArgumentParser(description="Generate test reports from test results")
    parser.add_argument("--input", "-i", help="Directory containing test outputs")
    parser.add_argument("--output", "-o", default="tests/reports", help="Directory to write reports to")
    parser.add_argument("--project", "-p", default="Codex-Arch", help="Project name")
    args = parser.parse_args()
    
    generator = TestReportGenerator(
        output_dir=args.output,
        input_dir=args.input,
        project_name=args.project
    )
    
    reports = generator.generate_reports()
    print("\nReports generated successfully!")
    print(f"HTML Report: {reports['html']}")
    print(f"JSON Report: {reports['json']}")
    

if __name__ == "__main__":
    main() 