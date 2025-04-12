# Git Hook Setup Guide

This guide explains how to set up Git hooks with Codex-Arch to automatically analyze your codebase during Git operations such as commits, merges, and pushes.

## What are Git Hooks?

Git hooks are scripts that Git executes before or after events such as commit, push, and merge. Codex-Arch provides pre-configured Git hooks that can:

1. Analyze code changes when commits are created
2. Generate updated architecture documentation on push
3. Validate architecture constraints before merges
4. Update dependency graphs when branches are merged

## Installing Git Hooks

### Automatic Installation

The simplest way to install Codex-Arch Git hooks is through the CLI:

```bash
codex-arch hooks install
```

This command automatically installs all recommended hooks to your repository's `.git/hooks` directory.

You can specify which hooks to install:

```bash
codex-arch hooks install --hooks pre-commit,post-merge
```

### Manual Installation

To manually install Git hooks:

1. Navigate to your project directory
2. Copy hook scripts from Codex-Arch to your Git hooks directory:

```bash
# Create a directory for your configuration
mkdir -p .codex-arch

# Copy hook configuration template
cp $(codex-arch hooks config-path) .codex-arch/hooks-config.yml

# Install specific hooks
codex-arch hooks install --config .codex-arch/hooks-config.yml
```

## Configuration

### Basic Configuration

Create a configuration file for your Git hooks:

```yaml
# .codex-arch/hooks-config.yml
hooks:
  pre-commit:
    enabled: true
    throttle: 300  # Run at most once every 5 minutes
    analyze:
      changed-files-only: true
      exclude: ["node_modules", "dist"]
    actions:
      - type: analyze
      - type: validate
        rules: ["no-circular-deps"]

  post-merge:
    enabled: true
    throttle: 600  # Run at most once every 10 minutes
    actions:
      - type: analyze
      - type: update-docs
        templates: ["dependency-graph", "summary"]
        
  pre-push:
    enabled: true
    actions:
      - type: validate
        rules: ["complexity-threshold", "dependency-limit"]
        fail-on-error: true
```

### Advanced Configuration

For more advanced use cases, you can customize every aspect of the hook behavior:

```yaml
# .codex-arch/hooks-config.yml
hooks:
  pre-commit:
    enabled: true
    throttle: 300
    conditions:
      - min-changes: 5  # Only run if at least 5 files changed
      - file-pattern: "*.py,*.js,src/**"  # Only run for these file patterns
    analyze:
      changed-files-only: true
      exclude: ["node_modules", "dist", "**/*.test.js"]
      metrics: ["complexity", "dependencies"]
    actions:
      - type: analyze
        output: ".codex-arch/latest-analysis.json"
      
      - type: validate
        rules:
          - name: "no-circular-deps"
            level: "error"
          - name: "complexity-threshold"
            level: "warning"
            threshold: 15
        
      - type: notify
        threshold: "warning"
        methods:
          - type: "console"
          - type: "file"
            path: ".codex-arch/validation-results.log"

environment:
  PYTHONPATH: "${PROJECT_ROOT}/src"
  MAX_MEMORY: "2G"
  
paths:
  output-dir: ".codex-arch/output"
  templates-dir: ".codex-arch/templates"
```

## Available Hooks

### Pre-Commit Hook

The pre-commit hook runs before a commit is completed:

- Analyzes changed files for architectural impacts
- Checks for violations of defined coding standards
- Can block commits that violate critical rules

### Post-Commit Hook

The post-commit hook runs after a commit is completed:

- Updates architecture documentation with latest changes
- Generates updated dependency graphs
- Can send notifications about architectural changes

### Pre-Push Hook

The pre-push hook runs before code is pushed to a remote:

- Performs full architecture validation
- Ensures code meets quality standards before it's shared
- Can prevent pushing code with architectural issues

### Post-Merge Hook

The post-merge hook runs after merging branches:

- Updates architecture artifacts after code is merged
- Regenerates documentation to include merged changes
- Can notify team members about significant architectural changes

## Hook Actions

Codex-Arch Git hooks support various actions:

| Action | Description |
|--------|-------------|
| `analyze` | Performs codebase analysis |
| `validate` | Validates against architectural rules |
| `update-docs` | Updates documentation artifacts |
| `notify` | Sends notifications about results |
| `export` | Exports analysis results to various formats |

## Rules Validation

You can define architectural rules to enforce standards:

```yaml
# .codex-arch/architecture-rules.yml
rules:
  - name: complexity-threshold
    description: "Maximum complexity per file"
    threshold: 15
    level: error
    
  - name: no-circular-deps
    description: "No circular dependencies allowed"
    level: error
    
  - name: dependency-limit
    description: "Maximum dependencies per file"
    threshold: 20
    level: warning
    
  - name: layer-isolation
    description: "Enforce clean architecture layers"
    level: error
    layers:
      - name: domain
        pattern: "src/domain/**"
      - name: application
        pattern: "src/application/**"
        allowed-deps: ["domain"]
      - name: infrastructure
        pattern: "src/infrastructure/**" 
        allowed-deps: ["domain", "application"]
      - name: presentation
        pattern: "src/presentation/**"
        allowed-deps: ["domain", "application"]
```

Reference this in your hooks configuration:

```yaml
# In your hooks-config.yml
hooks:
  pre-commit:
    # ...
    actions:
      - type: validate
        rules-file: ".codex-arch/architecture-rules.yml"
```

## Notification Options

Configure notifications for hook results:

```yaml
# In your hooks-config.yml
hooks:
  post-merge:
    # ...
    actions:
      - type: notify
        threshold: "warning"  # Only notify for warnings and errors
        methods:
          - type: "console"  # Standard console output
          
          - type: "file"  # Write to a file
            path: ".codex-arch/logs/hooks.log"
            
          - type: "slack"  # Send to Slack
            webhook: "${SLACK_WEBHOOK_URL}"
            channel: "#architecture"
            
          - type: "email"  # Send email
            recipients: ["team@example.com"]
            subject: "Architecture validation results"
            from: "codex-arch@example.com"
            
          - type: "custom"  # Custom script
            command: "./scripts/notify-team.sh ${RESULTS_FILE}"
```

## CI/CD Integration

For CI/CD pipelines, you can use Codex-Arch Git hooks programmatically:

```bash
# In your CI script
codex-arch hooks run pre-push --ci-mode
```

Or simply call the validation directly:

```bash
codex-arch validate --rules .codex-arch/architecture-rules.yml
```

## Troubleshooting

### Common Issues

1. **Hooks not running**

   Ensure hooks are executable:
   
   ```bash
   chmod +x .git/hooks/*
   ```

2. **Performance issues with large repositories**

   Configure throttling and selective analysis:
   
   ```yaml
   hooks:
     pre-commit:
       throttle: 600  # Run at most once every 10 minutes
       analyze:
         changed-files-only: true
   ```

3. **Hook configuration not found**

   Specify the configuration path explicitly:
   
   ```bash
   codex-arch hooks install --config /path/to/hooks-config.yml
   ```

### Debugging

Enable debug mode for verbose output:

```bash
CODEX_ARCH_DEBUG=1 git commit -m "Your commit message"
```

Check the log files:

```bash
cat .git/hooks/codex-arch.log
```

## Best Practices

1. **Start with minimal configuration** - Begin with just pre-commit hooks and basic validation
2. **Use throttling** - Prevent hooks from running too frequently
3. **Set appropriate thresholds** - Use warnings before errors
4. **Keep rules in version control** - Track architecture rules alongside code
5. **Use custom templates** - Customize documentation to fit your project's needs

## Reference

For a full reference of Git hook options and capabilities, see the [Git Hooks API Reference](../api/git-hooks.md). 