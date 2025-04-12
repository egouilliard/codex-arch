# Workflow Examples

This document illustrates how the various components of Codex-Arch work together in common usage scenarios and workflows. These examples will help you understand how to use the system effectively for different use cases.

## Basic Analysis Workflow

The most common workflow is analyzing a codebase to generate a comprehensive architecture report.

### Workflow Steps

1. **Initialization**: The CLI initializes the analysis process
2. **Configuration Loading**: Configuration is loaded from files or CLI arguments
3. **Extraction**: Extractors collect data from the codebase
4. **Analysis**: Analyzers process the extracted data to generate insights
5. **Metrics Calculation**: Metrics are calculated based on the analysis
6. **Visualization**: Visual representations are generated
7. **Summary Generation**: A comprehensive summary is created
8. **Output**: Results are delivered to the user

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CLI    │────▶│ File Tree  │────▶│ Analyzers │────▶│    Metrics   │
└──────────┘     │ Extractor  │     └───────────┘     └──────────────┘
                 └────────────┘                               │
                                                              │
                       ┌───────────┐                          │
                       │Dependency │◀───────────────────────┐ │
                       │ Extractor │                        │ │
                       └───────────┘                        │ │
                            │                               │ │
                            ▼                               │ ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐    │ ┌────────────────┐
│ Summary  │◀────│  Dependency   │◀────│ Visualization │◀───┘ │  Complexity    │
│ Builder  │     │   Analyzer    │     │ Generator     │      │  Calculator    │
└──────────┘     └───────────────┘     └──────────────┘      └────────────────┘
     │
     ▼
┌──────────┐
│  Output  │
└──────────┘
```

### CLI Usage Example

```bash
# Basic analysis with default settings
codex-arch analyze /path/to/project

# Analysis with specific configuration
codex-arch analyze --config=custom-config.yml /path/to/project

# Analysis with specific outputs
codex-arch analyze --output.format=html --output.directory=report /path/to/project

# Analysis focusing on specific aspects
codex-arch analyze --modules=dependencies,metrics --exclude="**/tests/**" /path/to/project
```

### Code Example

```python
from codex_arch import Analyzer

# Create analyzer with default configuration
analyzer = Analyzer()

# Run analysis
results = analyzer.analyze("/path/to/project")

# Access specific results
dependency_graph = results.dependency_graph
metrics = results.metrics
summary = results.summary

# Export results
results.export("report", format="html")
```

## Incremental Analysis Workflow

When working with a project over time, it's more efficient to perform incremental analysis on only the changed files.

### Workflow Steps

1. **Change Detection**: Detect what files have changed since the last analysis
2. **Cache Loading**: Load cached results from previous analysis
3. **Selective Extraction**: Extract data only from changed files
4. **Incremental Analysis**: Update analysis based on changes
5. **Result Update**: Update metrics, visualizations, and summaries
6. **Output**: Deliver updated results to the user

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CLI    │────▶│   Change   │────▶│   Cache   │────▶│   Selective  │
└──────────┘     │  Detector  │     │  Manager  │     │   Extractor  │
                 └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│  Output  │◀────│    Summary    │◀────│ Incremental  │◀────│    Analyzers   │
│          │     │    Builder    │     │ Updater      │     │                │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

### CLI Usage Example

```bash
# Incremental analysis based on Git changes
codex-arch analyze --incremental /path/to/project

# Incremental analysis with specific base commit
codex-arch analyze --incremental --base-commit=HEAD~10 /path/to/project

# Incremental analysis with manual file selection
codex-arch analyze --incremental --files="src/module1.py,src/module2.py" /path/to/project
```

### Code Example

```python
from codex_arch import IncrementalAnalyzer

# Create incremental analyzer
analyzer = IncrementalAnalyzer(cache_directory=".codex-cache")

# Run incremental analysis
results = analyzer.analyze(
    "/path/to/project",
    base_commit="HEAD~1",  # Compare against the previous commit
    changed_only=True      # Only analyze changed files
)

# Access and export results as in the basic workflow
```

## Git Hook Integration Workflow

Codex-Arch can be integrated with Git hooks to automatically analyze code changes during Git operations.

### Workflow Steps

1. **Hook Activation**: Git operation triggers a hook
2. **Change Detection**: Changed files are identified
3. **Focused Analysis**: Analysis is performed on the changed files
4. **Result Generation**: Focused results are generated
5. **Report**: A report is shown to the user or saved

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│   Git    │────▶│ Git Hook   │────▶│  Change   │────▶│   Focused    │
│  Event   │     │ Manager    │     │ Detector  │     │   Analyzer   │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
                      ┌────────────┐     ┌───────────────┐     ┌────────────────┐
                      │ Notification│◀────│    Result     │◀────│    Impact      │
                      │ Manager    │     │    Formatter  │     │    Analyzer    │
                      └────────────┘     └───────────────┘     └────────────────┘
```

### Setup Example

```bash
# Install Git hooks
codex-arch hooks install

# Configure hooks
codex-arch hooks config --pre-commit.enabled=true --post-merge.enabled=true

# Test hook manually
codex-arch hooks run pre-commit
```

### Configuration Example

```yaml
# codex-arch.yml
git_hooks:
  pre_commit:
    enabled: true
    analyze: true
    changed_only: true
    block_on_error: false
    summarize: true
  post_merge:
    enabled: true
    analyze: true
    notify: true
```

## API Integration Workflow

The REST API allows integration of Codex-Arch with other systems, such as CI/CD pipelines or developer tools.

### Workflow Steps

1. **API Request**: Client sends a request to the API
2. **Authentication**: Request is authenticated
3. **Request Processing**: The API processes the request
4. **Analysis Execution**: Analysis is performed as needed
5. **Response Generation**: Results are formatted for the response
6. **Response Delivery**: Results are sent back to the client

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│  Client  │────▶│ API Server │────▶│  Auth     │────▶│   Request    │
│  Request │     │            │     │  Manager  │     │   Handler    │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│  Client  │◀────│   Response    │◀────│   Result     │◀────│    Analysis    │
│ Response │     │   Formatter   │     │   Builder    │     │    Engine      │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

### API Usage Example

```bash
# Start the API server
codex-arch api start --port=8080

# Make a request to analyze a repository
curl -X POST \
     -H "Authorization: Bearer ${API_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"repository": "https://github.com/user/repo", "options": {"modules": ["dependencies"]}}' \
     http://localhost:8080/api/analyze
```

### Client Code Example

```python
import requests

# Make an API request
response = requests.post(
    "http://localhost:8080/api/analyze",
    headers={
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    },
    json={
        "repository": "https://github.com/user/repo",
        "options": {
            "modules": ["dependencies", "metrics"],
            "output": {"format": "json"}
        }
    }
)

# Process the response
results = response.json()
```

## Continuous Integration Workflow

Codex-Arch can be integrated into CI/CD pipelines to monitor code quality and architecture over time.

### Workflow Steps

1. **CI Trigger**: CI system triggers analysis
2. **Repository Checkout**: Code is checked out
3. **Analysis Execution**: Codex-Arch analyzes the code
4. **Threshold Checking**: Results are compared against thresholds
5. **Report Generation**: Reports are generated
6. **Notification**: Developers are notified of issues

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CI    │────▶│ Repository │────▶│  Codex    │────▶│   Analysis   │
│  System  │     │ Checkout   │     │  Executor │     │   Engine     │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│ Developer│◀────│ Notification  │◀────│  Report      │◀────│   Threshold    │
│ Notifier │     │ System        │     │  Generator   │     │   Checker      │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

### CI Configuration Example (GitHub Actions)

```yaml
# .github/workflows/architecture-analysis.yml
name: Architecture Analysis

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # Full git history for change detection
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install codex-arch
      
      - name: Run Architecture Analysis
        run: |
          codex-arch analyze \
            --output.format=json \
            --output.directory=analysis-results \
            --threshold.complexity.max=15 \
            --threshold.dependencies.circular=0 \
            --fail-on-threshold-exceeded=true \
            .
      
      - name: Upload Analysis Results
        uses: actions/upload-artifact@v2
        with:
          name: architecture-analysis
          path: analysis-results
```

## Custom Analysis Workflow

For specialized needs, Codex-Arch supports custom analysis through custom processors and plugins.

### Workflow Steps

1. **Custom Configuration**: User configures custom analysis
2. **Custom Processor Loading**: Custom processors are loaded
3. **Standard Analysis**: Standard analysis is performed
4. **Custom Processing**: Custom processors run on the data
5. **Result Integration**: Custom results are integrated
6. **Output**: Combined results are delivered

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CLI    │────▶│  Standard  │────▶│ Analysis  │────▶│   Custom     │
│          │     │  Analysis  │     │  Results  │     │   Processor  │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│  Output  │◀────│    Summary    │◀────│   Result     │◀────│    Custom      │
│          │     │    Builder    │     │   Integrator │     │    Results     │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

### Custom Processor Example

```python
# custom_processor.py
from codex_arch.processors import CustomProcessor

class SecurityAnalysisProcessor(CustomProcessor):
    """Custom processor for security analysis."""
    
    def process(self, context):
        """Process analysis results to identify security issues."""
        dependencies = context.get_result('dependencies')
        known_vulnerabilities = self.load_vulnerability_database()
        
        security_issues = []
        for dep in dependencies.external_dependencies:
            if dep.name in known_vulnerabilities:
                security_issues.append({
                    'module': dep.name,
                    'version': dep.version,
                    'vulnerability': known_vulnerabilities[dep.name]
                })
                
        return {
            'security_issues': security_issues,
            'total_issues': len(security_issues)
        }
        
    def load_vulnerability_database(self):
        """Load database of known vulnerabilities."""
        # Implementation would load from a file or API
        return {
            'unsecure-module': {
                'cve': 'CVE-2023-1234',
                'severity': 'high',
                'description': 'SQL injection vulnerability'
            }
        }
```

### Configuration Example

```yaml
# codex-arch.yml
processors:
  custom:
    - name: "security_analyzer"
      path: "./custom_processor.py"
      class: "SecurityAnalysisProcessor"
      enabled: true
      
output:
  # Include custom processor results in the report
  include_custom_results: true
```

### CLI Usage Example

```bash
# Run analysis with custom processor
codex-arch analyze --custom-processors=security_analyzer /path/to/project
```

## Feature Extraction Workflow

This workflow focuses on extracting specific features or patterns from the codebase.

### Workflow Steps

1. **Pattern Definition**: Define patterns to look for
2. **Code Extraction**: Extract code structure
3. **Pattern Matching**: Match patterns against the code
4. **Feature Extraction**: Extract features based on matches
5. **Output**: Generate feature-specific output

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CLI    │────▶│    Code    │────▶│  Pattern  │────▶│   Feature    │
│          │     │  Extractor │     │  Matcher  │     │   Extractor  │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                                              │
                                                              ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐
│  Output  │◀────│    Feature    │◀────│    Result    │
│          │     │    Report     │     │   Collector  │
└──────────┘     └───────────────┘     └──────────────┘
```

### CLI Usage Example

```bash
# Extract API endpoints
codex-arch extract --feature=api-endpoints /path/to/project

# Extract data models
codex-arch extract --feature=data-models --format=json /path/to/project

# Extract specific patterns
codex-arch extract --pattern="class.*Controller" --output=controllers.md /path/to/project
```

## Comparison Workflow

This workflow compares two versions of a codebase to analyze the architectural changes.

### Workflow Steps

1. **Version Selection**: Select two versions to compare
2. **Analysis**: Analyze both versions separately
3. **Comparison**: Compare the analysis results
4. **Difference Identification**: Identify significant differences
5. **Report Generation**: Generate comparison report

### Component Interaction

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌──────────────┐
│    CLI    │────▶│  Version   │────▶│ Analysis  │────▶│   Analysis   │
│          │     │  Selector  │     │ Version A │     │   Version B  │
└──────────┘     └────────────┘     └───────────┘     └──────────────┘
                                          │                  │
                                          └────────┬─────────┘
                                                   ▼
┌──────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
│  Output  │◀────│  Comparison   │◀────│   Result     │◀────│   Difference   │
│          │     │    Report     │     │   Compiler   │     │   Analyzer     │
└──────────┘     └───────────────┘     └──────────────┘     └────────────────┘
```

### CLI Usage Example

```bash
# Compare current code with a previous commit
codex-arch compare --base=HEAD~10 /path/to/project

# Compare two specific commits
codex-arch compare --base=v1.0.0 --target=v2.0.0 /path/to/project

# Compare specific aspects
codex-arch compare --base=main --target=feature-branch --modules=dependencies,metrics /path/to/project
```

## Next Steps

Now that you understand the common workflows, you can:

- Explore the [CLI Usage Guide](../guides/cli-usage.md) for more command examples
- Check out the [API Integration Guide](../guides/api-integration.md) for details on API usage
- See the [Advanced Use Cases](../guides/advanced-use-cases.md) for specialized workflows 