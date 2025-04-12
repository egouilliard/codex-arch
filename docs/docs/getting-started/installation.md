# Installation Guide

This guide will help you install Codex-Arch and its dependencies.

## Requirements

Before installing Codex-Arch, ensure you have the following prerequisites:

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control and change detection features)
- Graphviz (for visualization features)

## Installation Methods

### Using pip (Recommended)

The simplest way to install Codex-Arch is using pip:

```bash
pip install codex-arch
```

For a development installation with all optional dependencies:

```bash
pip install codex-arch[dev]
```

### From Source

To install from source:

```bash
# Clone the repository
git clone https://github.com/egouilliard/codex-arch

# Navigate to the directory
cd codex-arch

# Install the package
pip install -e .
```

## Platform-Specific Instructions

### Linux

Install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev graphviz

# CentOS/RHEL
sudo yum install python3-devel graphviz
```

### macOS

Install dependencies using Homebrew:

```bash
brew update
brew install python graphviz
```

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Graphviz from [graphviz.org](https://graphviz.org/download/)
3. Add the Graphviz bin directory to your PATH

## Verifying Installation

After installation, verify that Codex-Arch is correctly installed:

```bash
codex-arch --version
```

If the installation was successful, this should display the version number of Codex-Arch.

## Next Steps

Once you have successfully installed Codex-Arch, you can:

- Follow the [Quick Start Guide](quick-start.md) to begin using Codex-Arch
- Learn about [configuration options](configuration.md)
- Explore [use cases and examples](../guides/cli-usage.md)

## Troubleshooting

### Common Issues

#### Missing Dependencies

If you encounter errors related to missing dependencies, ensure you have installed all required packages:

```bash
pip install -r requirements.txt
```

#### Graphviz Not Found

If you receive an error indicating that Graphviz is not found:

1. Ensure Graphviz is installed on your system
2. Verify that the Graphviz executable is in your PATH
3. For Windows users, you may need to restart your terminal after adding Graphviz to PATH

#### Permission Errors

If you encounter permission errors during installation:

```bash
# Use --user flag
pip install --user codex-arch

# Or use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install codex-arch
```

For any other issues, please [file an issue](https://github.com/egouilliard/codex-arch) on the GitHub repository. 