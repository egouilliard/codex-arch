# Git Hooks Integration

Codex-Arch provides seamless integration with Git hooks to automatically analyze your codebase when changes occur. This enables real-time tracking of code architecture changes, dependency updates, and other metrics without requiring manual intervention.

## Overview

Git hooks are scripts that Git executes before or after events such as commit, push, and merge. Codex-Arch utilizes these hooks to:

- Automatically analyze code changes
- Track architectural evolution over time
- Generate incremental updates to dependency graphs
- Create change reports
- Notify team members of significant changes

## Supported Hooks

Codex-Arch supports the following Git hooks:

| Hook | Description |
|------|-------------|
| `post-commit` | Runs after a commit is created to analyze the changes |
| `post-merge` | Runs after a merge is completed to analyze the merged changes |
| `pre-push` | Runs before a push to ensure code quality and metrics are within defined limits |

## Installation

To install the Git hooks:

```bash
# Install hooks in the current repository
codex-arch hooks install

# Install hooks with custom configuration
codex-arch hooks install --config=/path/to/hooks-config.json
```

To uninstall the hooks:

```bash
codex-arch hooks uninstall
```

## Configuration

### Configuration File

The Git hook integration can be configured using a JSON configuration file. By default, Codex-Arch looks for a `.codex-hooks.json` file in the repository root, but you can specify a custom path.

Example configuration:

```json
{
  "enabled": true,
  "hooks": {
    "post-commit": true,
    "post-merge": true,
    "pre-push": false
  },
  "throttling": {
    "enabled": true,
    "min_interval": 300,
    "exclude_branches": ["main", "master"]
  },
  "analysis": {
    "depth": 2,
    "include": ["src/**/*.py", "lib/**/*.js"],
    "exclude": ["tests/**", "**/__pycache__/**"]
  },
  "notifications": {
    "enabled": true,
    "channels": ["slack", "email"],
    "threshold": "medium",
    "slack_webhook": "https://hooks.slack.com/services/...",
    "email": {
      "recipients": ["team@example.com"],
      "from": "codex-arch@example.com",
      "smtp_server": "smtp.example.com"
    }
  }
}
```

### Configuration Options

#### General Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Whether Git hooks are enabled |
| `hooks` | object | All enabled | Specify which hooks to enable/disable |

#### Throttling Options

Throttling prevents excessive analysis runs when many commits are made in a short time.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `throttling.enabled` | boolean | `true` | Whether throttling is enabled |
| `throttling.min_interval` | integer | `300` | Minimum seconds between analyses |
| `throttling.exclude_branches` | array | `[]` | Branches where throttling is disabled |

#### Analysis Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `analysis.depth` | integer | `2` | Depth of analysis (1-5, where 5 is most thorough) |
| `analysis.include` | array | All files | Glob patterns for files to include |
| `analysis.exclude` | array | Standard excludes | Glob patterns for files to exclude |

#### Notification Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `notifications.enabled` | boolean | `false` | Whether notifications are enabled |
| `notifications.channels` | array | `[]` | Notification channels to use |
| `notifications.threshold` | string | `"medium"` | Min severity for notifications (`low`, `medium`, `high`) |
| `notifications.slack_webhook` | string | `null` | Slack webhook URL |
| `notifications.email` | object | `{}` | Email notification settings |

## Using Git Hooks Programmatically

The Git hook functionality can also be used programmatically:

```python
from codex_arch.hooks import install_hooks, uninstall_hooks, HookConfig

# Create a custom hook configuration
config = HookConfig(
    enabled=True,
    hooks={
        "post-commit": True,
        "post-merge": True,
        "pre-push": False
    },
    throttling={
        "enabled": True,
        "min_interval": 300
    }
)

# Install hooks with custom configuration
install_hooks("/path/to/repo", config)

# Uninstall hooks
uninstall_hooks("/path/to/repo")
```

## Throttling Mechanism

The throttling mechanism prevents excessive analysis runs by tracking when the last analysis was performed. If a new commit occurs before the minimum interval has elapsed, the analysis is skipped.

### Manual Overrides

You can bypass throttling for important commits:

```bash
# Force analysis regardless of throttling
git commit -m "Important change" && codex-arch analyze --force
```

## Notification System

The notification system keeps your team informed about significant changes to the codebase architecture.

### Supported Notification Channels

- **Slack**: Sends notifications to a Slack channel via webhooks
- **Email**: Sends email notifications to specified recipients
- **Custom webhook**: Sends POST requests to a custom endpoint

### Notification Content

Notifications include:

- Summary of changes
- Link to detailed analysis
- Visual diff of dependency graphs (if available)
- Metrics changes

Example Slack notification:

```
*Codex-Arch Analysis Complete*
Repository: my-project
Commit: abc123 (Update authentication module)
Changes detected:
- 2 new dependencies added
- Complexity increased by 5%
- Cyclomatic complexity of auth.py increased from 12 to 18
View full report: https://codex-arch.example.com/reports/abc123
```

## Troubleshooting

### Common Issues

#### Hook Not Running

If hooks are not running:

1. Verify hooks are installed: `ls -la .git/hooks/`
2. Check that hooks are executable: `chmod +x .git/hooks/post-commit`
3. Ensure the configuration file exists and is valid
4. Check the logs in `.git/hooks/logs/`

#### Permission Denied

If you encounter permission errors:

```bash
# Make hooks executable
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-merge
chmod +x .git/hooks/pre-push
```

#### Throttling Issues

If analysis is being skipped due to throttling:

```bash
# Check the throttling status
codex-arch hooks throttle-status

# Reset the throttling timer
codex-arch hooks reset-throttle
```

## Advanced Configuration

### Custom Analysis Scripts

You can specify custom analysis scripts to run during hook execution:

```json
{
  "custom_scripts": {
    "pre-analysis": "/path/to/script-before-analysis.sh",
    "post-analysis": "/path/to/script-after-analysis.sh"
  }
}
```

### CI/CD Integration

For CI/CD environments, you may want to disable interactive prompts:

```json
{
  "non_interactive": true,
  "always_exit_success": true
}
```

## Next Steps

- [API Integration Guide](../guides/api-integration.md) for examples of using Git hooks with the API
- [Notifications Guide](../guides/notifications.md) for detailed configuration of notification channels
- [Custom Scripts Guide](../guides/custom-scripts.md) for creating custom analysis scripts 