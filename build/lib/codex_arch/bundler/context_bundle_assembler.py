"""
Context Bundle Assembler

This module provides the main ContextBundleAssembler class that collects all 
generated artifacts and packages them into a structured bundle for LLM consumption.
"""

import json
import os
import shutil
import time
import zipfile
import tarfile
import gzip
import glob
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from codex_arch.summary.data_collector import DataCollector
from codex_arch.summary.summary_builder import SummaryBuilder, SummaryConfig


class BundleConfig:
    """
    Configuration for the Context Bundle Assembler

    Provides configuration options for the artifact bundling process.
    """

    def __init__(
        self,
        bundle_dir: Optional[str] = None,
        include_file_tree: bool = True,
        include_dependencies: bool = True,
        include_metrics: bool = True,
        include_visualizations: bool = True,
        include_summaries: bool = True,
        cleanup_temp_files: bool = True,
        compress_bundle: bool = False,
        compression_format: str = 'zip'
    ):
        """
        Initialize BundleConfig.

        Args:
            bundle_dir: Directory to store the bundle (defaults to 'repo_meta')
            include_file_tree: Whether to include file tree artifacts
            include_dependencies: Whether to include dependency artifacts
            include_metrics: Whether to include metrics artifacts
            include_visualizations: Whether to include visualization artifacts
            include_summaries: Whether to include summary artifacts
            cleanup_temp_files: Whether to clean up temporary files after bundling
            compress_bundle: Whether to compress the bundle into a single file
            compression_format: Format for compression ('zip', 'tar', 'tar.gz')
        """
        self.bundle_dir = bundle_dir or 'repo_meta'
        self.include_file_tree = include_file_tree
        self.include_dependencies = include_dependencies
        self.include_metrics = include_metrics
        self.include_visualizations = include_visualizations
        self.include_summaries = include_summaries
        self.cleanup_temp_files = cleanup_temp_files
        self.compress_bundle = compress_bundle
        self.compression_format = compression_format
        
        # Validate compression format
        if compression_format not in ['zip', 'tar', 'tar.gz']:
            raise ValueError("Compression format must be one of 'zip', 'tar', or 'tar.gz'")

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BundleConfig':
        """
        Create a BundleConfig from a dictionary.

        Args:
            config_dict: Dictionary of configuration options

        Returns:
            BundleConfig instance
        """
        return cls(
            bundle_dir=config_dict.get('bundle_dir', 'repo_meta'),
            include_file_tree=config_dict.get('include_file_tree', True),
            include_dependencies=config_dict.get('include_dependencies', True),
            include_metrics=config_dict.get('include_metrics', True),
            include_visualizations=config_dict.get('include_visualizations', True),
            include_summaries=config_dict.get('include_summaries', True),
            cleanup_temp_files=config_dict.get('cleanup_temp_files', True),
            compress_bundle=config_dict.get('compress_bundle', False),
            compression_format=config_dict.get('compression_format', 'zip')
        )
    
    @classmethod
    def from_json_file(cls, file_path: str) -> 'BundleConfig':
        """
        Create a BundleConfig from a JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            BundleConfig instance
        """
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert BundleConfig to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            'bundle_dir': self.bundle_dir,
            'include_file_tree': self.include_file_tree,
            'include_dependencies': self.include_dependencies,
            'include_metrics': self.include_metrics,
            'include_visualizations': self.include_visualizations,
            'include_summaries': self.include_summaries,
            'cleanup_temp_files': self.cleanup_temp_files,
            'compress_bundle': self.compress_bundle,
            'compression_format': self.compression_format
        }

    def to_json_file(self, file_path: str) -> None:
        """
        Save BundleConfig to a JSON file.

        Args:
            file_path: Path to save configuration JSON
        """
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class ContextBundleAssembler:
    """
    Context Bundle Assembler

    Collects all generated artifacts and packages them into a structured
    bundle for LLM consumption.
    """

    def __init__(
        self,
        repo_path: str,
        output_dir: Optional[str] = None,
        config: Optional[Union[BundleConfig, Dict[str, Any]]] = None
    ):
        """
        Initialize the ContextBundleAssembler.

        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory containing generated artifacts (defaults to './output')
            config: Configuration options for bundle generation
        """
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'output')
        
        # Convert dictionary to BundleConfig if needed
        if isinstance(config, dict):
            self.config = BundleConfig.from_dict(config)
        elif config is None:
            self.config = BundleConfig()
        else:
            self.config = config
        
        # Prepare bundle directory path
        self.bundle_dir = os.path.join(
            self.output_dir, 
            self.config.bundle_dir
        )
        
        # Create bundle directory structure
        self._create_bundle_structure()
        
        # Track collected artifacts
        self.artifacts = {
            'file_tree': [],
            'dependencies': [],
            'metrics': [],
            'visualizations': [],
            'summaries': [],
            'manifest': None,
            'prompt_template': None
        }
        
        # Metadata for the bundle
        self.metadata = {
            'timestamp': datetime.now().isoformat(),
            'repository_path': self.repo_path,
            'repository_name': os.path.basename(self.repo_path),
            'tool_version': '1.0.0',  # Should be extracted from package version
            'bundle_id': f"codex-arch-{int(time.time())}"
        }

    def _create_bundle_structure(self) -> None:
        """
        Create the directory structure for the bundle.
        """
        # Create main bundle directory
        os.makedirs(self.bundle_dir, exist_ok=True)
        
        # Create subdirectories for different artifact types
        if self.config.include_file_tree:
            os.makedirs(os.path.join(self.bundle_dir, 'file_tree'), exist_ok=True)
        
        if self.config.include_dependencies:
            os.makedirs(os.path.join(self.bundle_dir, 'dependencies'), exist_ok=True)
        
        if self.config.include_metrics:
            os.makedirs(os.path.join(self.bundle_dir, 'metrics'), exist_ok=True)
        
        if self.config.include_visualizations:
            os.makedirs(os.path.join(self.bundle_dir, 'visualizations'), exist_ok=True)
        
        if self.config.include_summaries:
            os.makedirs(os.path.join(self.bundle_dir, 'summaries'), exist_ok=True)

    def _collect_file_tree_artifacts(self) -> List[str]:
        """
        Collect file tree artifacts.

        Returns:
            List of paths to collected artifacts
        """
        if not self.config.include_file_tree:
            return []
        
        artifact_paths = []
        
        # Look for file tree JSON and/or Markdown in output directory
        for filename in os.listdir(self.output_dir):
            if filename.startswith('file_tree') and (filename.endswith('.json') or filename.endswith('.md')):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(self.bundle_dir, 'file_tree', filename)
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected file tree artifact: {filename}")
        
        # If no file tree artifacts found, generate one
        if not artifact_paths:
            print("No existing file tree artifacts found, generating new ones...")
            from codex_arch.extractors.file_tree_extractor import FileTreeExtractor
            
            extractor = FileTreeExtractor(self.repo_path)
            
            # Generate JSON file tree
            json_tree = extractor.extract_file_tree(output_format='json')
            json_path = os.path.join(self.bundle_dir, 'file_tree', 'file_tree.json')
            with open(json_path, 'w') as f:
                json.dump(json_tree, f, indent=2)
            artifact_paths.append(json_path)
            
            # Generate Markdown file tree
            md_tree = extractor.extract_file_tree(output_format='markdown')
            md_path = os.path.join(self.bundle_dir, 'file_tree', 'file_tree.md')
            with open(md_path, 'w') as f:
                f.write(md_tree)
            artifact_paths.append(md_path)
        
        self.artifacts['file_tree'] = artifact_paths
        return artifact_paths
    
    def _collect_dependency_artifacts(self) -> List[str]:
        """
        Collect dependency artifacts.

        Returns:
            List of paths to collected artifacts
        """
        if not self.config.include_dependencies:
            return []
        
        artifact_paths = []
        
        # Look for dependency files in output directory
        for filename in os.listdir(self.output_dir):
            if (filename.startswith('dependency') or filename.startswith('python_dependencies')) and filename.endswith('.json'):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(self.bundle_dir, 'dependencies', filename)
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected dependency artifact: {filename}")
        
        # Also collect any DOT and SVG files that might be dependency graphs
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.dot') or filename.endswith('.svg'):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(self.bundle_dir, 'dependencies', filename)
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected dependency visualization: {filename}")
        
        # If no dependency artifacts found, we could generate them
        # But this would require running the dependency extractor which might be complex
        # For now, just print a warning
        if not artifact_paths:
            print("Warning: No dependency artifacts found in output directory")
        
        self.artifacts['dependencies'] = artifact_paths
        return artifact_paths
    
    def _collect_metrics_artifacts(self) -> List[str]:
        """
        Collect metrics artifacts.

        Returns:
            List of paths to collected artifacts
        """
        if not self.config.include_metrics:
            return []
        
        artifact_paths = []
        
        # Look for metrics files in output directory
        for filename in os.listdir(self.output_dir):
            if filename.startswith('metrics') and filename.endswith('.json'):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(self.bundle_dir, 'metrics', filename)
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected metrics artifact: {filename}")
        
        # If no metrics artifacts found, we could generate them
        # But for now, just print a warning
        if not artifact_paths:
            print("Warning: No metrics artifacts found in output directory")
        
        self.artifacts['metrics'] = artifact_paths
        return artifact_paths
    
    def _collect_visualization_artifacts(self) -> List[str]:
        """
        Collect visualization artifacts.

        Returns:
            List of paths to collected artifacts
        """
        if not self.config.include_visualizations:
            return []
        
        artifact_paths = []
        
        # Create visualizations directory if it doesn't exist
        viz_dir = os.path.join(self.bundle_dir, 'visualizations')
        os.makedirs(viz_dir, exist_ok=True)
        
        # Look for visualization files in output directory
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.svg') or filename.endswith('.png') or filename.endswith('.dot'):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(viz_dir, filename)
                
                # Skip if already copied to dependencies
                if os.path.exists(dest_path):
                    continue
                
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected visualization: {filename}")
        
        # Also check for any svg_test directory that might contain visualization files
        svg_test_dir = os.path.join(self.output_dir, 'svg_test')
        if os.path.isdir(svg_test_dir):
            for filename in os.listdir(svg_test_dir):
                if filename.endswith('.svg') or filename.endswith('.png'):
                    src_path = os.path.join(svg_test_dir, filename)
                    dest_path = os.path.join(viz_dir, filename)
                    shutil.copy2(src_path, dest_path)
                    artifact_paths.append(dest_path)
                    print(f"Collected visualization from svg_test: {filename}")
        
        self.artifacts['visualizations'] = artifact_paths
        return artifact_paths
    
    def _collect_summary_artifacts(self) -> List[str]:
        """
        Collect summary artifacts.

        Returns:
            List of paths to collected artifacts
        """
        if not self.config.include_summaries:
            return []
        
        artifact_paths = []
        
        # Look for summary files in output directory
        for filename in os.listdir(self.output_dir):
            if (filename.startswith('summary') or filename == 'complete_data.json') and (filename.endswith('.json') or filename.endswith('.md')):
                src_path = os.path.join(self.output_dir, filename)
                dest_path = os.path.join(self.bundle_dir, 'summaries', filename)
                shutil.copy2(src_path, dest_path)
                artifact_paths.append(dest_path)
                print(f"Collected summary artifact: {filename}")
        
        self.artifacts['summaries'] = artifact_paths
        return artifact_paths

    def collect_artifacts(self) -> Dict[str, List[str]]:
        """
        Collect all artifacts based on the configuration.

        Returns:
            Dictionary of collected artifact paths by type
        """
        print(f"Collecting artifacts for bundle in {self.bundle_dir}...")
        
        # Collect various artifact types
        self._collect_file_tree_artifacts()
        self._collect_dependency_artifacts()
        self._collect_metrics_artifacts()
        self._collect_visualization_artifacts()
        self._collect_summary_artifacts()
        
        return self.artifacts
    
    def generate_manifest(self) -> str:
        """
        Generate a manifest file that catalogs all included artifacts.

        Returns:
            Path to the generated manifest file
        """
        print("Generating manifest file...")
        
        # Make sure artifacts are collected
        if not any(self.artifacts.values()):
            self.collect_artifacts()
        
        # Prepare manifest data
        manifest = {
            'metadata': self.metadata,
            'artifacts': {},
            'artifact_count': 0
        }
        
        # Add artifact descriptions
        for artifact_type, paths in self.artifacts.items():
            if artifact_type in ['manifest', 'prompt_template']:
                continue
                
            if not paths:
                continue
                
            manifest['artifacts'][artifact_type] = []
            
            for path in paths:
                filename = os.path.basename(path)
                rel_path = os.path.relpath(path, self.bundle_dir)
                
                artifact_info = {
                    'filename': filename,
                    'path': rel_path,
                    'size_bytes': os.path.getsize(path),
                    'description': self._get_artifact_description(artifact_type, filename)
                }
                
                manifest['artifacts'][artifact_type].append(artifact_info)
                manifest['artifact_count'] += 1
        
        # Save manifest file
        manifest_path = os.path.join(self.bundle_dir, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self.artifacts['manifest'] = manifest_path
        print(f"Manifest file generated: {manifest_path}")
        
        return manifest_path
    
    def _get_artifact_description(self, artifact_type: str, filename: str) -> str:
        """
        Get a description for an artifact based on its type and filename.

        Args:
            artifact_type: Type of artifact
            filename: Name of the artifact file

        Returns:
            Description string
        """
        # File tree descriptions
        if artifact_type == 'file_tree':
            if filename.endswith('.json'):
                return "JSON representation of the repository file structure"
            elif filename.endswith('.md'):
                return "Markdown representation of the repository file structure"
        
        # Dependency descriptions
        elif artifact_type == 'dependencies':
            if 'python_dependencies' in filename:
                return "Python module dependencies extracted from the codebase"
            elif filename.endswith('.dot'):
                return "DOT graph representation of code dependencies"
            elif filename.endswith('.svg'):
                return "Visual representation of code dependencies"
        
        # Metrics descriptions
        elif artifact_type == 'metrics':
            return "Code metrics including complexity, line counts, and language distribution"
        
        # Visualization descriptions
        elif artifact_type == 'visualizations':
            if filename.endswith('.svg'):
                return "SVG visualization of code structure or dependencies"
            elif filename.endswith('.png'):
                return "PNG visualization of code structure or dependencies"
            elif filename.endswith('.dot'):
                return "DOT graph source for visualization"
        
        # Summary descriptions
        elif artifact_type == 'summaries':
            if filename == 'complete_data.json':
                return "Complete data collection including all extracted information"
            elif filename.endswith('.json'):
                return "JSON summary of the codebase structure and characteristics"
            elif filename.endswith('.md'):
                return "Markdown summary of the codebase structure and characteristics"
        
        # Default description
        return f"{artifact_type.capitalize()} artifact"
    
    def generate_prompt_template(self) -> str:
        """
        Generate a pre-prompt template that instructs LLMs on how to interpret the bundle.

        Returns:
            Path to the generated prompt template file
        """
        print("Generating pre-prompt template...")
        
        # Make sure manifest is generated
        if not self.artifacts.get('manifest'):
            self.generate_manifest()
        
        # Load manifest data
        with open(self.artifacts['manifest'], 'r') as f:
            manifest = json.load(f)
        
        # Generate prompt template
        prompt_template = f"""
# Codebase Analysis Context Bundle

This context bundle contains analysis artifacts for the repository: **{manifest['metadata']['repository_name']}**

## Bundle Metadata
- **Generated on:** {manifest['metadata']['timestamp']}
- **Bundle ID:** {manifest['metadata']['bundle_id']}
- **Tool Version:** {manifest['metadata']['tool_version']}

## Available Artifacts

This bundle contains {manifest['artifact_count']} artifacts organized by type:

"""
        
        # Add artifact sections
        for artifact_type, artifacts in manifest['artifacts'].items():
            if not artifacts:
                continue
                
            prompt_template += f"### {artifact_type.capitalize()} ({len(artifacts)})\n"
            
            for artifact in artifacts:
                prompt_template += f"- **{artifact['filename']}**: {artifact['description']}\n"
                prompt_template += f"  - Path: `{artifact['path']}`\n"
            
            prompt_template += "\n"
        
        # Add usage instructions
        prompt_template += """
## Interpretation Guide

When analyzing this codebase, please consider the following:

1. **File Structure**: The file tree provides an overview of the repository organization. Use this to understand the project layout.

2. **Dependencies**: Dependency graphs and files show relationships between modules. Look for highly connected modules as they are likely core components.

3. **Metrics**: Metrics provide quantitative insights about the codebase size, complexity, and language distribution.

4. **Visualizations**: Visual representations help understand complex relationships between components.

5. **Summaries**: Summary files provide high-level insights and analysis of the codebase architecture and patterns.

When providing code suggestions or architectural advice, refer to specific artifacts that informed your understanding. For example, "Based on the dependency graph, module X appears to be a central component..."

"""
        
        # Add specific instructions based on available artifacts
        has_python = any('python' in a['filename'] for artifacts in manifest['artifacts'].values() for a in artifacts)
        if has_python:
            prompt_template += """
### Python-Specific Guidelines
- Pay attention to import patterns and module organization
- Note the usage of any frameworks or libraries
- Consider how dependency structures might impact maintainability
"""
        
        # Save prompt template
        prompt_path = os.path.join(self.bundle_dir, 'prompt_template.md')
        with open(prompt_path, 'w') as f:
            f.write(prompt_template.strip())
        
        self.artifacts['prompt_template'] = prompt_path
        print(f"Pre-prompt template generated: {prompt_path}")
        
        return prompt_path
    
    def cleanup_temp_files(self) -> None:
        """
        Clean up temporary files that were generated during the analysis process.
        
        This removes interim files that are no longer needed after bundle creation.
        """
        if not self.config.cleanup_temp_files:
            print("Skipping cleanup of temporary files (disabled in config)")
            return
            
        print("Cleaning up temporary files...")
        
        # Define patterns for temp files
        temp_patterns = [
            os.path.join(self.output_dir, "*.tmp"),
            os.path.join(self.output_dir, "*.temp"),
            os.path.join(self.output_dir, "temp_*"),
            os.path.join(self.output_dir, "tmp_*")
        ]
        
        # Find and remove temp files
        removed_count = 0
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_count += 1
                    print(f"Removed temporary file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    removed_count += 1
                    print(f"Removed temporary directory: {file_path}")
        
        print(f"Cleanup complete: removed {removed_count} temporary files/directories")
    
    def compress_bundle(self) -> Optional[str]:
        """
        Compress the bundle directory into a single archive file.
        
        Returns:
            Path to the compressed bundle file, or None if compression is disabled
        """
        if not self.config.compress_bundle:
            print("Skipping bundle compression (disabled in config)")
            return None
            
        print(f"Compressing bundle using format: {self.config.compression_format}...")
        
        # Get base name for the archive
        archive_base = f"{os.path.basename(self.bundle_dir)}_{int(time.time())}"
        
        # Determine archive path based on format
        if self.config.compression_format == 'zip':
            archive_path = os.path.join(self.output_dir, f"{archive_base}.zip")
            self._create_zip_archive(archive_path)
            
        elif self.config.compression_format == 'tar':
            archive_path = os.path.join(self.output_dir, f"{archive_base}.tar")
            self._create_tar_archive(archive_path)
            
        elif self.config.compression_format == 'tar.gz':
            archive_path = os.path.join(self.output_dir, f"{archive_base}.tar.gz")
            self._create_tar_gz_archive(archive_path)
        
        # Update metadata
        self.metadata['compressed_bundle'] = os.path.basename(archive_path)
        self.metadata['compression_format'] = self.config.compression_format
        
        # If we've already generated a manifest, update it with the compression info
        if self.artifacts.get('manifest'):
            # Load existing manifest
            with open(self.artifacts['manifest'], 'r') as f:
                manifest = json.load(f)
            
            # Update metadata
            manifest['metadata']['compressed_bundle'] = os.path.basename(archive_path)
            manifest['metadata']['compression_format'] = self.config.compression_format
            
            # Save updated manifest
            with open(self.artifacts['manifest'], 'w') as f:
                json.dump(manifest, f, indent=2)
        
        print(f"Bundle compressed successfully: {archive_path}")
        return archive_path
    
    def _create_zip_archive(self, archive_path: str) -> None:
        """
        Create a ZIP archive of the bundle directory.
        
        Args:
            archive_path: Path where the archive will be saved
        """
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.bundle_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(self.bundle_dir))
                    zipf.write(file_path, arcname)
    
    def _create_tar_archive(self, archive_path: str) -> None:
        """
        Create a TAR archive of the bundle directory.
        
        Args:
            archive_path: Path where the archive will be saved
        """
        with tarfile.open(archive_path, 'w') as tar:
            tar.add(self.bundle_dir, arcname=os.path.basename(self.bundle_dir))
    
    def _create_tar_gz_archive(self, archive_path: str) -> None:
        """
        Create a compressed TAR.GZ archive of the bundle directory.
        
        Args:
            archive_path: Path where the archive will be saved
        """
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(self.bundle_dir, arcname=os.path.basename(self.bundle_dir))
    
    def finalize_bundle(self) -> Dict[str, Any]:
        """
        Finalize the bundle by collecting artifacts, generating manifest,
        prompt template, compressing, and cleaning up.
        
        Returns:
            Dictionary with bundle information including paths
        """
        # Step 1: Collect all artifacts
        self.collect_artifacts()
        
        # Step 2: Generate manifest
        manifest_path = self.generate_manifest()
        
        # Step 3: Generate prompt template
        prompt_path = self.generate_prompt_template()
        
        # Step 4: Compress bundle if enabled
        compressed_path = self.compress_bundle()
        
        # Step 5: Clean up temporary files if enabled
        self.cleanup_temp_files()
        
        # Return bundle information
        bundle_info = {
            'bundle_dir': self.bundle_dir,
            'manifest_path': manifest_path,
            'prompt_template_path': prompt_path,
            'artifacts': self.artifacts,
            'metadata': self.metadata
        }
        
        if compressed_path:
            bundle_info['compressed_path'] = compressed_path
        
        print(f"Bundle finalization complete: {self.bundle_dir}")
        return bundle_info 