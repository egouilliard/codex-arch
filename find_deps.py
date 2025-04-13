import json
import sys

def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else "cli/cli.py"
    
    with open('output/complete_dependencies.json') as f:
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

if __name__ == "__main__":
    main() 