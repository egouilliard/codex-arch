# Command-Line Interface (CLI) Reference

Codex-Arch provides a powerful command-line interface (CLI) that allows you to perform all architecture analysis operations directly from your terminal or scripts.

## Installation

The CLI is included when you install Codex-Arch:

```bash
# Install globally
pip install codex-arch

# Verify installation
codex-arch --version
```

## Global Options

These options apply to all commands:

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message and exit |
| `--verbose`, `-v` | Increase verbosity (can be used multiple times) |
| `--quiet`, `-q` | Suppress non-error output |
| `--config FILE` | Use a specific configuration file |
| `--output-format FORMAT` | Output format (json, yaml, text, markdown) |
| `--log-level LEVEL` | Set log level (debug, info, warning, error) |

## Core Commands

### analyze

Analyze a codebase and generate architecture reports.

```bash
codex-arch analyze [OPTIONS] [PATH]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--path PATH` | Path to the codebase to analyze (default: current directory) |
| `--exclude PATTERNS` | Patterns to exclude (comma-separated) |
| `--include PATTERNS` | Patterns to include (comma-separated) |
| `--output FILE` | Output file path (default: codex-arch-report.{format}) |
| `--format FORMAT` | Output format (json, markdown, html) |
| `--max-depth DEPTH` | Maximum directory depth (default: 10) |
| `--extractors EXTRACTORS` | Specific extractors to use (comma-separated) |
| `--no-cache` | Disable caching of analysis results |
| `--cache-dir DIR` | Directory to store cache files |

**Examples:**

```bash
# Analyze current directory
codex-arch analyze

# Analyze specific path with exclusions
codex-arch analyze --path /path/to/project --exclude "node_modules,*.pyc"

# Analyze with specific extractors and output format
codex-arch analyze --extractors "file-tree,python-deps" --format markdown --output report.md
```

### extract

Extract specific information from a codebase.

```bash
codex-arch extract [OPTIONS] [PATH]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--path PATH` | Path to the codebase to analyze (default: current directory) |
| `--extractors EXTRACTORS` | Specific extractors to use (comma-separated, required) |
| `--exclude PATTERNS` | Patterns to exclude (comma-separated) |
| `--include PATTERNS` | Patterns to include (comma-separated) |
| `--output FILE` | Output file path (default: codex-arch-extract.{format}) |
| `--format FORMAT` | Output format (json, markdown, html) |

**Examples:**

```bash
# Extract file tree
codex-arch extract --extractors file-tree

# Extract Python dependencies
codex-arch extract --extractors python-deps --exclude "tests/*,examples/*" --format json
```

### visualize

Generate visualizations from analysis results.

```bash
codex-arch visualize [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--input FILE` | Input file with analysis results |
| `--type TYPE` | Type of visualization (dependency-graph, treemap, sunburst) |
| `--output FILE` | Output file path (default: codex-arch-visual.{format}) |
| `--format FORMAT` | Output format (svg, png, pdf) |
| `--options JSON` | Visualization-specific options in JSON format |

**Examples:**

```bash
# Generate dependency graph
codex-arch visualize --input analysis.json --type dependency-graph --output deps.svg

# Generate treemap with custom options
codex-arch visualize --input analysis.json --type treemap --format png --options '{"group_by": "package", "color_by": "complexity"}'
```

### metrics

Calculate metrics for a codebase.

```bash
codex-arch metrics [OPTIONS] [PATH]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--path PATH` | Path to the codebase to analyze (default: current directory) |
| `--metrics METRICS` | Specific metrics to calculate (comma-separated) |
| `--exclude PATTERNS` | Patterns to exclude (comma-separated) |
| `--include PATTERNS` | Patterns to include (comma-separated) |
| `--output FILE` | Output file path (default: codex-arch-metrics.{format}) |
| `--format FORMAT` | Output format (json, markdown, html) |

**Examples:**

```bash
# Calculate all metrics
codex-arch metrics

# Calculate specific metrics
codex-arch metrics --metrics loc,complexity,dependencies --format json
```

### summary

Generate a summary of codebase analysis.

```bash
codex-arch summary [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--input FILE` | Input file with analysis results |
| `--output FILE` | Output file path (default: codex-arch-summary.{format}) |
| `--format FORMAT` | Output format (json, markdown, html) |
| `--detail-level LEVEL` | Detail level (brief, standard, detailed) |
| `--sections SECTIONS` | Specific sections to include (comma-separated) |

**Examples:**

```bash
# Generate standard summary
codex-arch summary --input analysis.json --format markdown

# Generate detailed summary with specific sections
codex-arch summary --input analysis.json --detail-level detailed --sections "overview,dependencies,complexity"
```

### changes

Analyze changes between two versions of a codebase.

```bash
codex-arch changes [OPTIONS] [PATH]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--path PATH` | Path to the codebase (default: current directory) |
| `--base-ref REF` | Base reference (commit/tag) |
| `--target-ref REF` | Target reference (commit/tag, defaults to current state) |
| `--extractors EXTRACTORS` | Specific extractors to use (comma-separated) |
| `--output FILE` | Output file path (default: codex-arch-changes.{format}) |
| `--format FORMAT` | Output format (json, markdown, html) |

**Examples:**

```bash
# Compare current state to a tag
codex-arch changes --base-ref v1.0.0

# Compare two specific commits
codex-arch changes --base-ref abc123 --target-ref def456 --format markdown
```

## Hook Commands

### hooks install

Install Git hooks for automatic analysis.

```bash
codex-arch hooks install [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--repo PATH` | Repository path (default: current directory) |
| `--hooks HOOKS` | Hooks to install (comma-separated, default: all) |
| `--config FILE` | Custom hooks configuration file |
| `--force` | Force overwrite existing hooks |

**Examples:**

```bash
# Install all hooks
codex-arch hooks install

# Install specific hooks
codex-arch hooks install --hooks post-commit,pre-push

# Install with custom configuration
codex-arch hooks install --config my-hooks-config.json
```

### hooks uninstall

Uninstall Git hooks.

```bash
codex-arch hooks uninstall [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--repo PATH` | Repository path (default: current directory) |
| `--hooks HOOKS` | Hooks to uninstall (comma-separated, default: all) |

**Examples:**

```bash
# Uninstall all hooks
codex-arch hooks uninstall

# Uninstall specific hooks
codex-arch hooks uninstall --hooks post-commit
```

## API Server Commands

### api serve

Start the API server.

```bash
codex-arch api serve [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--host HOST` | Host to bind to (default: 127.0.0.1) |
| `--port PORT` | Port to bind to (default: 5000) |
| `--workers NUM` | Number of worker processes (default: auto) |
| `--ssl-cert FILE` | SSL certificate file |
| `--ssl-key FILE` | SSL key file |
| `--auth TYPE` | Authentication type (api-key, jwt, oauth) |
| `--config FILE` | API server configuration file |

**Examples:**

```bash
# Start API server with default settings
codex-arch api serve

# Start API server with custom settings
codex-arch api serve --host 0.0.0.0 --port 8080 --workers 4

# Start API server with SSL
codex-arch api serve --ssl-cert cert.pem --ssl-key key.pem
```

### api key create

Create a new API key.

```bash
codex-arch api key create [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--name NAME` | Name of the API key |
| `--scopes SCOPES` | Permission scopes (comma-separated) |
| `--expires DAYS` | Expiration in days (default: never) |

**Examples:**

```bash
# Create API key with default settings
codex-arch api key create --name "CI Server"

# Create API key with specific scopes and expiration
codex-arch api key create --name "Read-only Key" --scopes read --expires 30
```

### api key list

List all API keys.

```bash
codex-arch api key list [OPTIONS]
```

**Examples:**

```bash
# List all API keys
codex-arch api key list
```

### api key revoke

Revoke an API key.

```bash
codex-arch api key revoke [OPTIONS] KEY_ID
```

**Examples:**

```bash
# Revoke API key
codex-arch api key revoke abc123
```

## Extractor Commands

### extractors list

List available extractors.

```bash
codex-arch extractors list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--details` | Show detailed information for each extractor |

**Examples:**

```bash
# List all extractors
codex-arch extractors list

# List extractors with details
codex-arch extractors list --details
```

## Visualization Commands

### visualizations list

List available visualization types.

```bash
codex-arch visualizations list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--details` | Show detailed information for each visualization type |

**Examples:**

```bash
# List all visualization types
codex-arch visualizations list

# List visualization types with details
codex-arch visualizations list --details
```

## Metrics Commands

### metrics list

List available metrics.

```bash
codex-arch metrics list [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--details` | Show detailed information for each metric |

**Examples:**

```bash
# List all available metrics
codex-arch metrics list

# List metrics with details
codex-arch metrics list --details
```

## Config Commands

### config init

Initialize a configuration file.

```bash
codex-arch config init [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--output FILE` | Output file path (default: .codex-arch.json) |
| `--force` | Overwrite existing file |

**Examples:**

```bash
# Create a default configuration file
codex-arch config init

# Create a configuration file at a specific location
codex-arch config init --output config/codex-arch.json
```

### config validate

Validate a configuration file.

```bash
codex-arch config validate [OPTIONS] [FILE]
```

**Examples:**

```bash
# Validate the default configuration file
codex-arch config validate

# Validate a specific configuration file
codex-arch config validate custom-config.json
```

## Environment Variables

The CLI respects the following environment variables:

| Variable | Description |
|----------|-------------|
| `CODEX_ARCH_CONFIG` | Path to configuration file |
| `CODEX_ARCH_API_KEY` | API key for authentication |
| `CODEX_ARCH_API_URL` | URL of the API server |
| `CODEX_ARCH_OUTPUT_FORMAT` | Default output format |
| `CODEX_ARCH_LOG_LEVEL` | Default log level |
| `CODEX_ARCH_CACHE_DIR` | Directory for cache files |

## Exit Codes

The CLI uses the following exit codes:

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Command line parsing error |
| 3 | Configuration error |
| 4 | Authentication error |
| 5 | Connection error |
| 6 | Timeout error |
| 7 | Validation error |

## Configuration File

The CLI configuration file can be in JSON, YAML, or TOML format. The default location is `.codex-arch.json` in the current directory or the user's home directory.

Example configuration file:

```json
{
  "general": {
    "output_format": "json",
    "log_level": "info",
    "cache_dir": ".codex-arch-cache"
  },
  "analysis": {
    "exclude": ["node_modules", "*.pyc", ".git"],
    "include": ["src/**/*", "lib/**/*"],
    "max_depth": 10
  },
  "api": {
    "url": "https://your-server/api/v1",
    "auth": {
      "type": "api-key",
      "key": "your-api-key"
    }
  },
  "hooks": {
    "enabled": true,
    "post-commit": true,
    "post-merge": true,
    "pre-push": false,
    "throttling": {
      "enabled": true,
      "min_interval": 300
    }
  }
}
```

## Usage in Scripts

The CLI is designed to be easily used in scripts:

```bash
#!/bin/bash
# Example script to analyze multiple repositories

REPOS=("repo1" "repo2" "repo3")

for repo in "${REPOS[@]}"; do
  echo "Analyzing $repo..."
  
  codex-arch analyze --path "/path/to/$repo" --output "reports/$repo-analysis.json" --format json
  
  if [ $? -ne 0 ]; then
    echo "Error analyzing $repo"
    exit 1
  fi
  
  codex-arch visualize --input "reports/$repo-analysis.json" \
    --type dependency-graph --output "reports/$repo-deps.svg"
    
  codex-arch summary --input "reports/$repo-analysis.json" \
    --format markdown --output "reports/$repo-summary.md"
done

echo "All repositories analyzed successfully!"
```

## Next Steps

- Review the [API Endpoints Reference](endpoints.md) for more details on the REST API
- Learn about [Git Hooks Integration](git-hooks.md) for automated analysis
- See the [API Integration Guide](../guides/api-integration.md) for programmatic usage examples 