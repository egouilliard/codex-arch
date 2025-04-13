"""
Summary Builder Module

This module provides the main SummaryBuilder class that coordinates the
collection of data and generation of summaries, with configuration options.
"""

import json
import os
from typing import Dict, Any, Optional, List, Union

from codex_arch.summary.data_collector import DataCollector
from codex_arch.summary.templates import TemplateRenderer
from codex_arch.summary.smart_summarizer import SmartSummarizer


class SummaryConfig:
    """
    Configuration for the Summary Builder

    Provides configuration options for the summary generation process.
    """

    def __init__(
        self,
        detail_level: str = 'standard',
        output_formats: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        focus_areas: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        include_visualizations: bool = True,
        custom_templates: Optional[Dict[str, str]] = None,
        # Additional parameters used by CLI
        template: str = 'standard',
        include_metrics: bool = True,
        include_dependencies: bool = True,
        use_smart_summarization: bool = True,
        exclude_dirs: Optional[List[str]] = None
    ):
        """
        Initialize SummaryConfig.

        Args:
            detail_level: Level of detail in summary ('minimal', 'standard', or 'detailed')
            output_formats: List of output formats ('markdown', 'json')
            ignore_patterns: Patterns to ignore in file tree
            focus_areas: Areas to focus on ('dependencies', 'complexity', 'structure')
            output_dir: Directory to store output files
            include_visualizations: Whether to include visualizations
            custom_templates: Custom templates for summary generation
            template: Template to use for summary generation (CLI parameter)
            include_metrics: Whether to include metrics in the summary (CLI parameter)
            include_dependencies: Whether to include dependencies in the summary (CLI parameter)
            use_smart_summarization: Whether to use smart summarization (CLI parameter)
            exclude_dirs: Directories to exclude from analysis (CLI parameter)
        """
        self.detail_level = detail_level
        self.output_formats = output_formats or ['markdown', 'json']
        self.ignore_patterns = ignore_patterns or [
            '.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd',
            'venv', 'env', '.env', 'node_modules'
        ]
        self.focus_areas = focus_areas or ['dependencies', 'complexity', 'structure']
        self.output_dir = output_dir
        self.include_visualizations = include_visualizations
        self.custom_templates = custom_templates or {}
        
        # Set CLI-specific parameters
        self.template = template
        self.include_metrics = include_metrics
        self.include_dependencies = include_dependencies
        self.use_smart_summarization = use_smart_summarization
        self.exclude_dirs = exclude_dirs or []
        
        # If exclude_dirs is provided, add them to ignore_patterns
        if exclude_dirs:
            for dir_name in exclude_dirs:
                if dir_name not in self.ignore_patterns:
                    self.ignore_patterns.append(dir_name)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SummaryConfig':
        """
        Create a SummaryConfig from a dictionary.

        Args:
            config_dict: Dictionary of configuration options

        Returns:
            SummaryConfig instance
        """
        # Get default ignore patterns if not provided
        default_ignore_patterns = [
            '.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd',
            'venv', 'env', '.env', 'node_modules'
        ]
        
        # Get default focus areas if not provided
        default_focus_areas = ['dependencies', 'complexity', 'structure']
        
        # Use the same defaults as in __init__ for consistent behavior
        return cls(
            detail_level=config_dict.get('detail_level', 'standard'),
            output_formats=config_dict.get('output_formats', ['markdown', 'json']),
            ignore_patterns=config_dict.get('ignore_patterns', default_ignore_patterns),
            focus_areas=config_dict.get('focus_areas', default_focus_areas),
            output_dir=config_dict.get('output_dir'),
            include_visualizations=config_dict.get('include_visualizations', True),
            custom_templates=config_dict.get('custom_templates', {}),
            template=config_dict.get('template', 'standard'),
            include_metrics=config_dict.get('include_metrics', True),
            include_dependencies=config_dict.get('include_dependencies', True),
            use_smart_summarization=config_dict.get('use_smart_summarization', True),
            exclude_dirs=config_dict.get('exclude_dirs', [])
        )

    @classmethod
    def from_json_file(cls, file_path: str) -> 'SummaryConfig':
        """
        Create a SummaryConfig from a JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            SummaryConfig instance
        """
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert SummaryConfig to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            'detail_level': self.detail_level,
            'output_formats': self.output_formats,
            'ignore_patterns': self.ignore_patterns,
            'focus_areas': self.focus_areas,
            'output_dir': self.output_dir,
            'include_visualizations': self.include_visualizations,
            'custom_templates': self.custom_templates,
            'template': self.template,
            'include_metrics': self.include_metrics,
            'include_dependencies': self.include_dependencies,
            'use_smart_summarization': self.use_smart_summarization,
            'exclude_dirs': self.exclude_dirs
        }

    def to_json_file(self, file_path: str) -> None:
        """
        Save SummaryConfig to a JSON file.

        Args:
            file_path: Path to save configuration JSON
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class SummaryBuilder:
    """
    Summary Builder

    Coordinates data collection, analysis, and summary generation with
    configuration options for customization.
    """

    def __init__(
        self,
        repo_path: str,
        config: Optional[Union[SummaryConfig, Dict[str, Any]]] = None
    ):
        """
        Initialize the SummaryBuilder.

        Args:
            repo_path: Path to the repository to analyze
            config: Configuration options for summary generation
        """
        self.repo_path = os.path.abspath(repo_path)
        
        # Convert dictionary to SummaryConfig if needed
        if isinstance(config, dict):
            self.config = SummaryConfig.from_dict(config)
        elif config is None:
            self.config = SummaryConfig()
        else:
            self.config = config
        
        # Initialize components
        self.data_collector = DataCollector(
            repo_path=self.repo_path,
            output_dir=self.config.output_dir
        )
        
        # Data and output references
        self.data = None
        self.markdown_path = None
        self.json_path = None
        self.insights = None

    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from all extractors and analyzers.

        Returns:
            Complete data structure with all collected information
        """
        print("Collecting data for summary generation...")
        self.data = self.data_collector.collect_all(
            ignore_patterns=self.config.ignore_patterns
        )
        return self.data

    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate insights from the collected data.

        Returns:
            Dictionary of insights
        """
        # Ensure data is collected
        if not self.data:
            self.collect_data()
        
        print("Generating insights...")
        smart_summarizer = SmartSummarizer(self.data)
        self.insights = smart_summarizer.generate_insights()
        
        # Add insights to the data
        self.data['insights'] = self.insights
        
        return self.insights

    def generate_summaries(
        self,
        markdown_file: Optional[str] = None,
        json_file: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate summaries in the configured formats.

        Args:
            markdown_file: Override path for Markdown output
            json_file: Override path for JSON output

        Returns:
            Dictionary of output file paths by format
        """
        # Ensure data and insights are collected/generated
        if not self.data:
            self.collect_data()
        
        if 'insights' not in self.data:
            self.generate_insights()
        
        print("Generating summaries...")
        template_renderer = TemplateRenderer(self.data)
        
        output_files = {}
        
        # Generate Markdown if configured
        if 'markdown' in self.config.output_formats:
            self.markdown_path = template_renderer.save_markdown(markdown_file)
            output_files['markdown'] = self.markdown_path
            print(f"Generated Markdown summary: {self.markdown_path}")
        
        # Generate JSON if configured
        if 'json' in self.config.output_formats:
            self.json_path = template_renderer.save_json(json_file)
            output_files['json'] = self.json_path
            print(f"Generated JSON summary: {self.json_path}")
        
        return output_files

    def generate_smart_summary_text(self) -> str:
        """
        Generate a smart textual summary of the insights.

        Returns:
            Human-readable summary text
        """
        # Ensure insights are generated
        if 'insights' not in self.data:
            self.generate_insights()
        
        smart_summarizer = SmartSummarizer(self.data)
        return smart_summarizer.generate_summary_text()

    def run(
        self,
        markdown_file: Optional[str] = None,
        json_file: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Run the complete summary generation process.

        Args:
            markdown_file: Override path for Markdown output
            json_file: Override path for JSON output

        Returns:
            Dictionary of output file paths by format
        """
        print(f"Starting summary generation for {self.repo_path}")
        print(f"Using detail level: {self.config.detail_level}")
        print(f"Focus areas: {', '.join(self.config.focus_areas)}")
        
        # Collect data
        self.collect_data()
        
        # Generate insights
        self.generate_insights()
        
        # Generate summaries
        output_files = self.generate_summaries(markdown_file, json_file)
        
        print("Summary generation complete!")
        for fmt, path in output_files.items():
            print(f"Generated {fmt.upper()} summary: {path}")
        
        return output_files

    @classmethod
    def create_with_default_config(cls, repo_path: str) -> 'SummaryBuilder':
        """
        Create a SummaryBuilder with default configuration.

        Args:
            repo_path: Path to the repository to analyze

        Returns:
            SummaryBuilder instance with default configuration
        """
        return cls(repo_path, SummaryConfig())

    @classmethod
    def create_from_config_file(cls, repo_path: str, config_file: str) -> 'SummaryBuilder':
        """
        Create a SummaryBuilder from a configuration file.

        Args:
            repo_path: Path to the repository to analyze
            config_file: Path to configuration JSON file

        Returns:
            SummaryBuilder instance with the loaded configuration
        """
        config = SummaryConfig.from_json_file(config_file)
        return cls(repo_path, config)


# Command-line interface function for direct invocation
def main():
    """
    Command-line entry point for the Summary Builder.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate codebase summary')
    parser.add_argument('repo_path', help='Path to the repository to analyze')
    parser.add_argument('--config', help='Path to configuration JSON file')
    parser.add_argument('--output-dir', help='Directory to store output files')
    parser.add_argument('--detail-level', choices=['minimal', 'standard', 'detailed'],
                      default='standard', help='Level of detail in summary')
    parser.add_argument('--formats', nargs='+', choices=['markdown', 'json'],
                      default=['markdown', 'json'], help='Output formats')
    parser.add_argument('--ignore', nargs='+', help='Patterns to ignore in file tree')
    parser.add_argument('--focus', nargs='+', help='Areas to focus on')
    
    args = parser.parse_args()
    
    # Create builder from config file if provided
    if args.config:
        builder = SummaryBuilder.create_from_config_file(args.repo_path, args.config)
    else:
        # Create a custom configuration from arguments
        config = SummaryConfig(
            detail_level=args.detail_level,
            output_formats=args.formats,
            ignore_patterns=args.ignore,
            focus_areas=args.focus,
            output_dir=args.output_dir
        )
        builder = SummaryBuilder(args.repo_path, config)
    
    # Run the summary generation
    builder.run()


if __name__ == '__main__':
    main() 