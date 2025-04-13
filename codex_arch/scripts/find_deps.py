import json
import sys
import os
from pathlib import Path

def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else "cli/cli.py"
    
    # Get project root path (two directories up from this script)
    project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    deps_file = project_root / 'output' / 'complete_dependencies.json'
    
    if not deps_file.exists():
        print(f"Error: Dependencies file not found at {deps_file}")
        print("Make sure to run the dependency analysis first.")
        return 1
    
    with open(deps_file) as f:
        data = json.load(f)
    
    # Find what the target file depends on
    print(f"\nDependencies of {target_file}:")
    if target_file in data['edges']:
        for dep in data['edges'][target_file]:
            print(f"  - {dep}")
    else:
        print("  No dependencies found")
    
    # Find what depends on the target file
    print(f"\nFiles that depend on {target_file}:")
    depends_on_target = []
    for file, deps in data['edges'].items():
        if target_file in deps:
            depends_on_target.append(file)
    
    if depends_on_target:
        for file in depends_on_target:
            print(f"  - {file}")
    else:
        print("  No files depend on this")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 