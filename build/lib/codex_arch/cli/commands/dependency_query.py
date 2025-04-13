import json
import sys
import click
from pathlib import Path

@click.command()
@click.argument('file_path')
@click.option('--dependency-file', '-d', default='output/complete_dependencies.json', 
              help='Path to the dependency JSON file')
@click.option('--direction', '-dir', type=click.Choice(['in', 'out', 'both']), default='both',
              help='Direction of dependencies to show: in=reverse deps, out=direct deps, both=all')
def query(file_path, dependency_file, direction):
    """
    Query dependencies for a specific file.
    
    Shows files that depend on the given file (reverse dependencies) and
    files that the given file depends on (direct dependencies).
    """
    try:
        with open(dependency_file) as f:
            data = json.load(f)
        
        # Direct dependencies (what file_path depends on)
        if direction in ['out', 'both']:
            print(f"\nDependencies of {file_path}:")
            if file_path in data['edges']:
                for dep in data['edges'][file_path]:
                    print(f"  - {dep}")
            else:
                print("  No dependencies found")
        
        # Reverse dependencies (what depends on file_path)
        if direction in ['in', 'both']:
            print(f"\nFiles that depend on {file_path}:")
            depends_on_target = []
            for file, deps in data['edges'].items():
                if file_path in deps:
                    depends_on_target.append(file)
            
            if depends_on_target:
                for file in depends_on_target:
                    print(f"  - {file}")
            else:
                print("  No files depend on this")
                
        return 0
    except FileNotFoundError:
        print(f"Error: Dependency file '{dependency_file}' not found.")
        return 1
    except KeyError as e:
        print(f"Error: Missing key in dependency file: {e}")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    query() 