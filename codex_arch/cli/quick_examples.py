"""
Quick examples for the Codex-Arch CLI.
"""

QUICK_EXAMPLES = """
Common Codex-Arch Commands:
===========================

Setup:
  source venv/bin/activate

Extract Dependencies:
  codex-arch dependencies my_project --output analysis_results

Visualize Dependencies:
  codex-arch visualize analysis_results/python_dependencies.json --output dependency_graph.svg

Generate File Tree:
  codex-arch filetree my_project --output project_structure.json

Collect Code Metrics:
  codex-arch metrics my_project --output project_metrics.json

Run Full Analysis:
  codex-arch analyze my_project --output full_analysis --exclude-dirs venv .git node_modules

View All Options:
  codex-arch <command> --help

See docs/quick_reference.md for more examples and common workflows.
"""

def get_examples():
    """Return the quick examples string."""
    return QUICK_EXAMPLES 