# Configuration

This guide explains how to configure Codex-Arch for your specific needs and workflows.

## Configuration Files

Codex-Arch supports multiple configuration methods:

1. **Project configuration file**: `codex-arch.yml` or `codex-arch.json` in the project root
2. **User configuration file**: `~/.codex-arch/config.yml` or `~/.codex-arch/config.json`
3. **Environment variables**: Prefixed with `CODEX_ARCH_`
4. **Command-line arguments**: Takes precedence over all other configuration methods

Configuration is loaded in the order listed above, with later methods overriding earlier ones.

## Configuration Format

Codex-Arch configuration can be defined in YAML or JSON format. The following examples use YAML for readability.

### Basic Configuration

```yaml
# codex-arch.yml
project:
  name: "My Project"
  description: "A sample project for Codex-Arch"

analysis:
  include:
    - "src/**/*.py"
    - "lib/**/*.py"
  exclude:
    - "**/*_test.py"
    - "**/vendor/**"
    - "**/node_modules/**"
    - "**/__pycache__/**"
    - "**/*.pyc"

output:
  format: "markdown"
  directory: "codex-output"
  bundle: true
```

## Configuration Sections

### Project Settings

```yaml
project:
  name: "My Project"                    # Project name (default: directory name)
  description: "Project description"    # Project description
  version: "1.0.0"                      # Project version
  repository: "https://github.com/..."  # Repository URL
```

### Analysis Settings

```yaml
analysis:
  include:                              # File patterns to include (glob format)
    - "src/**/*.py"
    - "lib/**/*.js"
  exclude:                              # File patterns to exclude
    - "**/*_test.py"
    - "**/node_modules/**"
  max_file_size: 1048576                # Maximum file size to analyze (in bytes)
  follow_symlinks: false                # Whether to follow symbolic links
  include_hidden: false                 # Whether to include hidden files
  max_depth: 10                         # Maximum directory depth to analyze
  languages:                            # Language-specific settings
    python:
      ignore_imports:                   # Imports to ignore in dependency analysis
        - "typing"
        - "logging"
      resolve_external: true            # Resolve external dependencies
      include_stdlib: false             # Include standard library in analysis
    javascript:
      parse_jsx: true                   # Process JSX files
      resolve_node_modules: false       # Resolve npm dependencies
```

### Metrics Settings

```yaml
metrics:
  collect:                              # Metrics to collect
    - "loc"                             # Lines of code
    - "complexity"                      # Complexity metrics
    - "dependencies"                    # Dependency metrics
  loc:
    count_blank_lines: false            # Whether to count blank lines
    count_comments: false               # Whether to count comment lines
  complexity:
    max_warning: 10                     # Complexity value to trigger warning
    max_error: 20                       # Complexity value to trigger error
  custom:                               # Custom metrics configuration
    - name: "my_metric"
      script: "./scripts/custom_metric.py"
      threshold: 5
```

### Visualization Settings

```yaml
visualization:
  graphs:
    dependency:                         # Dependency graph configuration
      format: "svg"                     # Output format (svg, png, dot)
      direction: "LR"                   # Graph direction (LR, TB, RL, BT)
      include_external: false           # Include external dependencies
      cluster_by_package: true          # Group nodes by package
      style:                            # Visual styling
        node:
          shape: "box"
          color: "#4285f4"
        edge:
          color: "#999999"
        cluster:
          color: "#e0e0e0"
    structure:                          # Structure graph configuration
      format: "svg"
      direction: "TB"
      show_methods: true
      show_attributes: true
```

### Output Settings

```yaml
output:
  format: "markdown"                    # Output format (markdown, html, json)
  directory: "codex-output"             # Output directory
  bundle: true                          # Bundle all outputs into a zip file
  clean: true                           # Clean output directory before generating
  reports:                              # Configure which reports to generate
    summary: true                       # Overall project summary
    dependencies: true                  # Dependency report
    metrics: true                       # Metrics report
    changes: false                      # Changes report (requires Git)
  templates:                            # Custom report templates
    summary: "./templates/summary.jinja"
    dependencies: "./templates/deps.jinja"
```

### Git Hook Settings

```yaml
git_hooks:
  pre_commit:                           # Configure pre-commit hook
    enabled: true                       # Enable pre-commit hook
    analyze: true                       # Run analysis on commit
    changed_only: true                  # Analyze only changed files
    block_on_error: false               # Block commit on errors
  post_merge:                           # Configure post-merge hook
    enabled: true                       # Enable post-merge hook
    analyze: true                       # Run analysis after merge
    notify: true                        # Show desktop notification
```

### API Settings

```yaml
api:
  enabled: false                        # Enable API server
  host: "localhost"                     # API server host
  port: 8080                            # API server port
  auth:                                 # Authentication configuration
    type: "token"                       # Authentication type (none, token, jwt)
    token: "your-secret-token"          # API token (if auth.type is "token")
    jwt_secret: "your-jwt-secret"       # JWT secret (if auth.type is "jwt")
  cors:                                 # CORS configuration
    enabled: true                       # Enable CORS
    origins:                            # Allowed origins
      - "http://localhost:3000"
```

### Caching Settings

```yaml
cache:
  enabled: true                         # Enable caching
  directory: ".codex-arch-cache"        # Cache directory
  ttl: 86400                            # Cache TTL in seconds (default: 1 day)
  invalidate_on_changes: true           # Invalidate cache on file changes
```

## Environment Variables

All configuration options can also be set using environment variables prefixed with `CODEX_ARCH_` and using underscores to separate nested properties:

```bash
# Example environment variables
export CODEX_ARCH_PROJECT_NAME="My Project"
export CODEX_ARCH_ANALYSIS_INCLUDE="src/**/*.py,lib/**/*.js"
export CODEX_ARCH_ANALYSIS_EXCLUDE="**/*_test.py,**/node_modules/**"
export CODEX_ARCH_OUTPUT_FORMAT="markdown"
export CODEX_ARCH_OUTPUT_DIRECTORY="codex-output"
export CODEX_ARCH_API_ENABLED=true
export CODEX_ARCH_API_PORT=9000
```

## Command-Line Arguments

Configuration options can also be provided as command-line arguments, which take precedence over all other methods:

```bash
# Example command-line usage
codex-arch analyze --project.name="My Project" \
                   --analysis.include="src/**/*.py,lib/**/*.js" \
                   --analysis.exclude="**/*_test.py,**/node_modules/**" \
                   --output.format=markdown \
                   --output.directory=codex-output
```

## Configuration Inheritance

You can use the `extends` property to inherit configuration from another file:

```yaml
# codex-arch.yml
extends: "./base-config.yml"

# Override specific settings
output:
  format: "html"
```

## Configuration Examples

### Minimal Configuration

```yaml
# codex-arch.yml (minimal)
analysis:
  include:
    - "**/*.py"
  exclude:
    - "**/test_*.py"
    - "**/__pycache__/**"

output:
  format: "markdown"
  directory: "codex-output"
```

### Complete Analysis Configuration

```yaml
# codex-arch.yml (comprehensive)
project:
  name: "Advanced Project"
  description: "A complex project with custom configuration"
  version: "2.1.0"
  repository: "https://github.com/user/advanced-project"

analysis:
  include:
    - "src/**/*.py"
    - "lib/**/*.js"
    - "web/**/*.html"
  exclude:
    - "**/*_test.py"
    - "**/node_modules/**"
    - "**/dist/**"
    - "**/__pycache__/**"
    - "**/*.pyc"
  max_file_size: 2097152
  follow_symlinks: false
  include_hidden: false
  max_depth: 15
  languages:
    python:
      ignore_imports:
        - "typing"
        - "logging"
        - "os"
        - "sys"
      resolve_external: true
      include_stdlib: false
    javascript:
      parse_jsx: true
      resolve_node_modules: false
      ignore_imports:
        - "react"
        - "lodash"

metrics:
  collect:
    - "loc"
    - "complexity"
    - "dependencies"
    - "custom"
  loc:
    count_blank_lines: false
    count_comments: true
  complexity:
    max_warning: 15
    max_error: 25
  custom:
    - name: "test_coverage"
      script: "./scripts/coverage_metric.py"
      threshold: 80

visualization:
  graphs:
    dependency:
      format: "svg"
      direction: "LR"
      include_external: true
      cluster_by_package: true
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
      format: "svg"
      direction: "TB"
      show_methods: true
      show_attributes: true
      style:
        node:
          shape: "ellipse"
          color: "#34a853"
        edge:
          color: "#666666"
          style: "solid"

output:
  format: "html"
  directory: "codex-output"
  bundle: true
  clean: true
  reports:
    summary: true
    dependencies: true
    metrics: true
    changes: true
  templates:
    summary: "./templates/custom_summary.jinja"
    dependencies: "./templates/custom_deps.jinja"
    metrics: "./templates/custom_metrics.jinja"

git_hooks:
  pre_commit:
    enabled: true
    analyze: true
    changed_only: true
    block_on_error: true
    summarize: true
  post_merge:
    enabled: true
    analyze: true
    notify: true
    report: true

api:
  enabled: true
  host: "0.0.0.0"
  port: 8080
  auth:
    type: "jwt"
    jwt_secret: "${JWT_SECRET}"
    expiration: 3600
  cors:
    enabled: true
    origins:
      - "http://localhost:3000"
      - "https://myapp.example.com"
  rate_limit:
    enabled: true
    max_requests: 100
    window_seconds: 60

cache:
  enabled: true
  directory: ".codex-arch-cache"
  ttl: 86400
  invalidate_on_changes: true
  compression: true
```

## Troubleshooting

### Common Configuration Issues

#### Invalid Configuration Format
If you encounter errors related to configuration parsing, check the syntax of your YAML or JSON file. Common issues include:
- Missing quotes around strings with special characters
- Incorrect indentation in YAML files
- Trailing commas in JSON files

#### Path Resolution Problems
When using relative paths in your configuration, they are resolved relative to the configuration file's location. If you experience path resolution issues:
- Try using absolute paths
- Verify the file or directory exists
- Check file permissions

#### Environment Variable Substitution
You can use environment variable substitution in your configuration files:

```yaml
api:
  port: ${PORT:-8080}    # Use PORT env var, default to 8080 if not set
  auth:
    token: ${API_TOKEN}  # Use API_TOKEN env var
```

If variables are not being substituted:
- Check that the variable is defined in your environment
- Verify the syntax for variable substitution

## Next Steps

Now that you understand how to configure Codex-Arch, you can:

- Explore the [CLI Usage Guide](../guides/cli-usage.md) to learn how to use the command-line interface
- Read the [API Integration Guide](../guides/api-integration.md) if you plan to use the REST API
- Check out the [Git Hook Setup](../guides/git-hook-setup.md) for automated analysis 