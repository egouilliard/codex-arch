# Advanced Use Cases

This guide covers advanced and specialized use cases for Codex-Arch, demonstrating how to leverage its capabilities for complex scenarios and integrations.

## Monorepo Analysis

Analyzing monorepos requires special considerations due to their size and complexity.

### Optimized Analysis Strategy

```bash
codex-arch analyze /path/to/monorepo \
  --exclude "node_modules,dist,build,**/test/**" \
  --chunking enabled \
  --memory-optimized \
  --cache-results
```

### Workspace-Specific Analysis

For monorepos with multiple workspaces:

```bash
codex-arch analyze /path/to/monorepo \
  --focus "packages/core-services" \
  --include-dependencies \
  --output-dir "./analysis/core-services"
```

### Cross-Workspace Dependencies

Generate a workspace dependency graph:

```bash
codex-arch workspace-graph /path/to/monorepo \
  --workspace-pattern "packages/*" \
  --include-external-deps \
  --output monorepo-workspace-diagram.svg
```

## Architecture Compliance Monitoring

### Defining Architecture Rules

Create a rules file to enforce architectural boundaries:

```yaml
# architecture-rules.yml
rules:
  - name: layered-architecture
    type: layering
    layers:
      - name: presentation
        pattern: "src/presentation/**"
      - name: application
        pattern: "src/application/**"
      - name: domain
        pattern: "src/domain/**"
      - name: infrastructure
        pattern: "src/infrastructure/**"
    allowed_dependencies:
      - from: presentation
        to: [application]
      - from: application
        to: [domain]
      - from: infrastructure
        to: [application, domain]

  - name: module-boundaries
    type: modularity
    modules:
      - name: user
        pattern: "src/**/user/**"
      - name: product
        pattern: "src/**/product/**"
      - name: order
        pattern: "src/**/order/**"
    loose_coupling: true
```

### Validating Architecture Rules

```bash
codex-arch validate /path/to/project \
  --rules architecture-rules.yml \
  --report-format html \
  --output architecture-compliance-report.html
```

### CI Integration for Compliance Checks

```bash
#!/bin/bash
# In your CI pipeline

# Run architecture validation
codex-arch validate /path/to/project \
  --rules architecture-rules.yml \
  --exit-on-violation \
  --report-format junit \
  --output architecture-test-results.xml

# Check exit code
if [ $? -ne 0 ]; then
  echo "Architecture validation failed!"
  exit 1
fi
```

## Time-Based Analysis and Evolution Tracking

### Analyzing Code Evolution

```bash
codex-arch timeline /path/to/project \
  --start-date "2023-01-01" \
  --end-date "2023-12-31" \
  --interval "month" \
  --metrics "complexity,dependencies,size" \
  --output code-evolution.json
```

### Generating Evolution Visualizations

```bash
codex-arch visualize-timeline ./code-evolution.json \
  --type "line-chart" \
  --metrics "complexity,dependencies" \
  --output complexity-evolution.svg
```

### Comparing Architecture Between Versions

```bash
codex-arch diff-architecture \
  --base-version "v1.0.0" \
  --target-version "v2.0.0" \
  --format detailed \
  --output architecture-changes.md
```

## Custom Metrics and Analysis Extensions

### Defining Custom Metrics

Create a custom metrics plugin:

```python
# custom_metrics.py
from codex_arch.plugins import MetricsPlugin

class SecurityMetricsPlugin(MetricsPlugin):
    def name(self):
        return "security-metrics"
    
    def calculate(self, file_content, file_path, context):
        security_score = 0
        
        # Check for hardcoded secrets
        if "password" in file_content.lower() or "secret" in file_content.lower():
            security_score -= 10
            
        # Check for proper error handling
        if "try" in file_content and "except Exception:" in file_content:
            security_score -= 5
            
        # Check for secure imports
        if "import ssl" in file_content or "import cryptography" in file_content:
            security_score += 5
            
        return {
            "security_score": security_score,
            "has_hardcoded_secrets": "password" in file_content.lower() or "secret" in file_content.lower(),
            "has_proper_error_handling": "except Exception:" not in file_content
        }
```

### Using Custom Metrics

```bash
codex-arch analyze /path/to/project \
  --plugin-path ./custom_metrics.py \
  --metrics "complexity,dependencies,security-metrics" \
  --output ./analysis-with-security.json
```

### Creating Custom Visualizations

```python
# custom_visualizer.py
from codex_arch.plugins import VisualizationPlugin
import matplotlib.pyplot as plt
import numpy as np

class SecurityHeatmapPlugin(VisualizationPlugin):
    def name(self):
        return "security-heatmap"
    
    def visualize(self, analysis_results, output_path, options=None):
        # Extract security metrics
        files = []
        scores = []
        
        for file_path, metrics in analysis_results["files"].items():
            if "security_score" in metrics:
                files.append(file_path.split("/")[-1])  # Just filename
                scores.append(metrics["security_score"])
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        
        # Sort by score
        indices = np.argsort(scores)
        files = [files[i] for i in indices]
        scores = [scores[i] for i in indices]
        
        # Create heatmap
        plt.barh(files, scores, color=plt.cm.RdYlGn(np.array(scores) / 20 + 0.5))
        plt.xlabel("Security Score")
        plt.title("Security Assessment by File")
        plt.grid(axis="x")
        
        plt.tight_layout()
        plt.savefig(output_path)
        
        return output_path
```

### Using Custom Visualizations

```bash
codex-arch visualize ./analysis-with-security.json \
  --plugin-path ./custom_visualizer.py \
  --type security-heatmap \
  --output security-heatmap.png
```

## Integration with External Tools

### GitHub Integration

```python
# GitHub workflow example
import requests
import json
import os
import subprocess

# Run Codex-Arch analysis
subprocess.run([
    "codex-arch", "analyze", "./", 
    "--output", "architecture-analysis.json"
])

# Load analysis results
with open("architecture-analysis.json", "r") as f:
    analysis = json.load(f)

# Post to GitHub as PR comment
pr_number = os.environ.get("PR_NUMBER")
token = os.environ.get("GITHUB_TOKEN")
repo = os.environ.get("GITHUB_REPOSITORY")

# Generate summary
summary = f"""
## Architecture Analysis

- Files analyzed: {analysis['metrics']['total_files']}
- Complexity score: {analysis['metrics']['complexity']['average']:.2f}
- Dependencies: {len(analysis['dependencies'])}
- High-risk modules: {sum(1 for m in analysis['modules'] if m['risk_score'] > 7)}

[View complete analysis](https://your-dashboard.example.com/analysis/{analysis['id']})
"""

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
data = {"body": summary}

requests.post(url, headers=headers, json=data)
```

### Jira Integration

Creating Jira tickets for architectural refactoring:

```python
# Jira integration example
from jira import JIRA
import json

# Authentication
jira = JIRA(
    server='https://your-jira-instance.atlassian.net',
    basic_auth=('email@example.com', 'API_TOKEN')
)

# Load analysis results
with open("architecture-analysis.json", "r") as f:
    analysis = json.load(f)

# Find high-complexity modules that need refactoring
complex_modules = []
for module, metrics in analysis["modules"].items():
    if metrics["complexity"] > 25:  # Threshold for high complexity
        complex_modules.append({
            "name": module,
            "complexity": metrics["complexity"],
            "dependencies": metrics["dependencies"],
            "files": metrics["files"]
        })

# Create Jira tickets for refactoring tasks
for module in complex_modules:
    issue_dict = {
        'project': {'key': 'ARCH'},
        'summary': f'Refactor high-complexity module: {module["name"]}',
        'description': f'''
        This module has high complexity and should be refactored.
        
        Complexity score: {module["complexity"]}
        Dependencies: {module["dependencies"]}
        Number of files: {len(module["files"])}
        
        Key files:
        {chr(10).join(["- " + f for f in module["files"][:5]])}
        
        See complete analysis: https://your-dashboard.example.com/modules/{module["name"]}
        ''',
        'issuetype': {'name': 'Task'},
        'priority': {'name': 'High'},
        'labels': ['refactoring', 'architecture', 'tech-debt']
    }
    
    new_issue = jira.create_issue(fields=issue_dict)
    print(f"Created issue {new_issue.key} for module {module['name']}")
```

## Architecture Documentation Generation

### Creating Architecture Decision Records (ADRs)

```bash
# Generate summary of architectural decisions based on code structure
codex-arch adr-suggest /path/to/project \
  --output ./docs/architecture/adrs/
```

### Generating Architecture Documentation Site

```bash
# Generate comprehensive documentation
codex-arch generate-docs /path/to/project \
  --template comprehensive \
  --output ./architecture-docs \
  --include-visualizations \
  --include-metrics \
  --include-evolution
```

### Custom Documentation Templates

```yaml
# custom-doc-template.yml
template:
  name: "Custom Architecture Documentation"
  sections:
    - title: "Executive Summary"
      content:
        - type: "text"
          template: |
            # {{ project_name }} Architecture
            
            This document provides an architectural overview of the {{ project_name }} system.
            
            ## Key Metrics
            
            - **Files:** {{ metrics.total_files }}
            - **Lines of Code:** {{ metrics.lines_of_code }}
            - **Complexity:** {{ metrics.complexity.average }}
            - **Modules:** {{ modules | length }}
            
        - type: "chart"
          chart_type: "pie"
          data_source: "language_distribution"
          title: "Language Distribution"
          
    - title: "Module Structure"
      content:
        - type: "module_list"
          include_metrics: true
          sort_by: "complexity"
          
        - type: "visualization"
          visualization: "module_dependency_graph"
          options:
            layout: "hierarchical"
            
    - title: "Hotspots Analysis"
      content:
        - type: "hotspots"
          metric: "complexity"
          limit: 10
          
        - type: "hotspots"
          metric: "dependencies"
          limit: 10
          
    - title: "Recommendations"
      content:
        - type: "recommendations"
          include_refactoring: true
```

Using the custom template:

```bash
codex-arch generate-docs /path/to/project \
  --template-file ./custom-doc-template.yml \
  --output ./custom-architecture-docs
```

## Performance Optimization for Large Codebases

### Parallel Processing

```bash
codex-arch analyze /path/to/large-codebase \
  --parallel \
  --workers 8 \
  --chunk-size 1000 \
  --memory-limit 8G
```

### Incremental Analysis

```bash
# First run - full analysis with caching
codex-arch analyze /path/to/large-codebase \
  --cache-dir ./.codex-arch/cache \
  --output ./analysis-results.json

# Later runs - incremental analysis
codex-arch analyze /path/to/large-codebase \
  --incremental \
  --cache-dir ./.codex-arch/cache \
  --previous-results ./analysis-results.json \
  --output ./updated-analysis.json
```

### Focused Analysis

```bash
# Analyze only specific areas
codex-arch analyze /path/to/large-codebase \
  --focus "src/critical-module/**" \
  --include-dependencies \
  --depth 2
```

## Continuous Architecture Quality Monitoring

### Setting Up Architecture Quality Gates

```yaml
# architecture-quality.yml
quality_gates:
  - name: "complexity"
    threshold: 15
    scope: "file"
    action: "fail"
    
  - name: "dependencies"
    threshold: 25
    scope: "file"
    action: "warn"
    
  - name: "circular_dependencies"
    threshold: 0
    scope: "project"
    action: "fail"
    
  - name: "dead_code"
    threshold: 5%
    scope: "project"
    action: "warn"
    
  - name: "layering_violations"
    threshold: 0
    scope: "project"
    action: "fail"
```

### Implementing Quality Gates in CI/CD

```bash
#!/bin/bash
# quality-gate.sh

SEVERITY=0

# Run architecture analysis
codex-arch analyze ./ \
  --output analysis.json

# Check quality gates
codex-arch check-quality \
  --quality-gates architecture-quality.yml \
  --analysis analysis.json \
  --report quality-report.json

# Extract severity from report
VIOLATIONS=$(jq '.failed_gates | length' quality-report.json)
if [ $VIOLATIONS -gt 0 ]; then
  # Get highest severity
  SEVERITY=$(jq '.exit_code' quality-report.json)
  
  # Print report
  echo "Architecture quality check failed with $VIOLATIONS violations!"
  jq -r '.failed_gates[] | "❌ " + .name + ": " + .message' quality-report.json
else
  echo "✅ Architecture quality checks passed!"
fi

exit $SEVERITY
```

## Integration with AI for Advanced Insights

### Using the Codex-Arch AI Extension

```bash
# Install AI extension
pip install codex-arch-ai

# Generate AI-powered architecture insights
codex-arch ai-insights /path/to/project \
  --model "gpt-4" \
  --api-key "your-api-key" \
  --focus "architecture-patterns" \
  --output architecture-insights.md
```

### Sample AI-Generated Insights

AI-powered analysis can identify:

1. Hidden architectural patterns
2. Potential refactoring opportunities
3. Technical debt hotspots
4. Architecture anti-patterns
5. Recommendations for architectural improvements

### Custom AI Prompts

```yaml
# custom-ai-prompts.yml
prompts:
  - name: "dependency-analysis"
    template: |
      Analyze the following dependency graph for potential issues, architectural smells, and improvement opportunities:
      
      {{dependency_graph}}
      
      Focus on:
      1. Identifying circular dependencies
      2. Modules with excessive incoming or outgoing dependencies
      3. Potential modularization opportunities
      4. Architecture layering violations
      
  - name: "code-complexity"
    template: |
      Review the following code complexity metrics and suggest refactoring priorities:
      
      {{complexity_metrics}}
      
      Provide:
      1. Top 3 modules that should be refactored first
      2. Specific refactoring techniques that would be most effective
      3. Risk assessment of the current complexity levels
```

Using custom prompts:

```bash
codex-arch ai-insights /path/to/project \
  --prompt-file custom-ai-prompts.yml \
  --prompt-name "dependency-analysis" \
  --output ai-dependency-analysis.md
```

## Conclusion

These advanced use cases demonstrate the flexibility and power of Codex-Arch for complex architectural analysis, monitoring, and documentation. By leveraging these patterns and integrations, you can create sophisticated workflows tailored to your specific needs.

For further assistance or custom integrations, contact the Codex-Arch team or refer to our [community forums](https://github.com/egouilliard/codex-arch/discussions). 