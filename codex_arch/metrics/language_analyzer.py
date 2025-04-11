"""
Language Analyzer Module.

This module provides functionality to analyze programming language distribution
in a codebase based on file extensions and patterns.
"""

from typing import Dict, Set, List, Tuple, Optional, Any
from pathlib import Path

# Mapping of file extensions to language names
LANGUAGE_MAP = {
    # Python
    '.py': 'Python',
    '.pyi': 'Python',
    '.pyx': 'Python',
    '.pyw': 'Python',
    
    # JavaScript and TypeScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',
    
    # Web
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SCSS',
    '.less': 'LESS',
    
    # C-family
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.cxx': 'C++',
    '.cc': 'C++',
    '.hpp': 'C++',
    '.hxx': 'C++',
    '.c++': 'C++',
    '.h++': 'C++',
    '.cs': 'C#',
    
    # JVM languages
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    '.groovy': 'Groovy',
    '.scala': 'Scala',
    '.clj': 'Clojure',
    
    # Ruby
    '.rb': 'Ruby',
    '.rake': 'Ruby',
    '.gemspec': 'Ruby',
    
    # PHP
    '.php': 'PHP',
    '.phtml': 'PHP',
    
    # Go
    '.go': 'Go',
    
    # Rust
    '.rs': 'Rust',
    
    # Swift
    '.swift': 'Swift',
    
    # Shell scripting
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.fish': 'Shell',
    '.bat': 'Batch',
    '.cmd': 'Batch',
    '.ps1': 'PowerShell',
    
    # Data formats
    '.json': 'JSON',
    '.xml': 'XML',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.csv': 'CSV',
    '.tsv': 'TSV',
    
    # Documentation
    '.md': 'Markdown',
    '.rst': 'reStructuredText',
    '.txt': 'Text',
    '.tex': 'LaTeX',
    
    # Configuration
    '.ini': 'INI',
    '.conf': 'Config',
    '.cfg': 'Config',
    '.env': 'Environment',
    
    # Other languages
    '.pl': 'Perl',
    '.pm': 'Perl',
    '.lua': 'Lua',
    '.r': 'R',
    '.dart': 'Dart',
    '.elm': 'Elm',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hrl': 'Erlang',
    '.hs': 'Haskell',
}

# Language family categories
LANGUAGE_FAMILIES = {
    'Scripting': {'Python', 'JavaScript', 'Ruby', 'PHP', 'Perl', 'Lua', 'Shell', 'Batch', 'PowerShell'},
    'Compiled': {'C', 'C++', 'Go', 'Rust', 'Swift', 'Java', 'Kotlin', 'C#'},
    'Web': {'HTML', 'CSS', 'SCSS', 'LESS', 'JavaScript', 'TypeScript', 'PHP'},
    'JVM': {'Java', 'Kotlin', 'Scala', 'Groovy', 'Clojure'},
    'Data/Configuration': {'JSON', 'XML', 'YAML', 'TOML', 'INI', 'Config', 'CSV', 'TSV'},
    'Documentation': {'Markdown', 'Text', 'reStructuredText', 'LaTeX'},
    'Systems': {'C', 'C++', 'Rust'},
    'Mobile': {'Swift', 'Kotlin', 'Java', 'Dart', 'Objective-C'},
    'Functional': {'Haskell', 'Scala', 'Clojure', 'Elixir', 'Erlang', 'Elm'}
}

def get_language_for_extension(extension: str) -> str:
    """
    Get the programming language name for a file extension.
    
    Args:
        extension: The file extension including the dot, e.g., '.py'
        
    Returns:
        The language name or 'Other' if not recognized
    """
    return LANGUAGE_MAP.get(extension.lower(), 'Other')

def get_language_family(language: str) -> Set[str]:
    """
    Get the language family/families for a language.
    
    Args:
        language: The language name
        
    Returns:
        Set of family names the language belongs to
    """
    families = set()
    for family, langs in LANGUAGE_FAMILIES.items():
        if language in langs:
            families.add(family)
    return families

def analyze_language_distribution(
    file_counts_by_extension: Dict[str, int], 
    line_counts_by_extension: Dict[str, int]
) -> Dict[str, Any]:
    """
    Analyze language distribution based on file extensions.
    
    Args:
        file_counts_by_extension: Dictionary mapping extensions to file counts
        line_counts_by_extension: Dictionary mapping extensions to line counts
        
    Returns:
        Dictionary with language distribution analysis
    """
    # Initialize results
    result = {
        "by_language": {
            "files": {},
            "lines": {}
        },
        "by_family": {
            "files": {},
            "lines": {}
        },
        "top_languages": [],
        "language_breakdown": {}
    }
    
    # Calculate total values
    total_files = sum(file_counts_by_extension.values())
    total_lines = sum(line_counts_by_extension.values())
    
    # Group by language name instead of extension
    language_files = {}
    language_lines = {}
    
    for ext, count in file_counts_by_extension.items():
        language = get_language_for_extension(ext)
        language_files[language] = language_files.get(language, 0) + count
        
    for ext, count in line_counts_by_extension.items():
        language = get_language_for_extension(ext)
        language_lines[language] = language_lines.get(language, 0) + count
    
    # Calculate percentages by language
    if total_files > 0:
        for language, count in language_files.items():
            result["by_language"]["files"][language] = round((count / total_files) * 100, 2)
            
    if total_lines > 0:
        for language, count in language_lines.items():
            result["by_language"]["lines"][language] = round((count / total_lines) * 100, 2)
    
    # Calculate family distribution
    family_files = {}
    family_lines = {}
    
    for language, count in language_files.items():
        families = get_language_family(language)
        for family in families:
            family_files[family] = family_files.get(family, 0) + count
            
    for language, count in language_lines.items():
        families = get_language_family(language)
        for family in families:
            family_lines[family] = family_lines.get(family, 0) + count
    
    # Calculate percentages by family
    if total_files > 0:
        for family, count in family_files.items():
            result["by_family"]["files"][family] = round((count / total_files) * 100, 2)
            
    if total_lines > 0:
        for family, count in family_lines.items():
            result["by_family"]["lines"][family] = round((count / total_lines) * 100, 2)
    
    # Get top languages by line count
    sorted_languages = sorted(
        [(language, count) for language, count in language_lines.items()],
        key=lambda x: x[1], 
        reverse=True
    )
    
    result["top_languages"] = [
        {"name": lang, "lines": count, "percentage": result["by_language"]["lines"][lang]}
        for lang, count in sorted_languages[:5]  # Top 5 languages
    ]
    
    # Generate language breakdown with extensions
    language_extensions = {}
    for ext in file_counts_by_extension:
        language = get_language_for_extension(ext)
        if language not in language_extensions:
            language_extensions[language] = []
        language_extensions[language].append(ext)
    
    for language, extensions in language_extensions.items():
        file_count = language_files.get(language, 0)
        line_count = language_lines.get(language, 0)
        
        result["language_breakdown"][language] = {
            "file_count": file_count,
            "line_count": line_count,
            "file_percentage": result["by_language"]["files"].get(language, 0),
            "line_percentage": result["by_language"]["lines"].get(language, 0),
            "extensions": extensions,
            "families": list(get_language_family(language))
        }
    
    return result 