"""
Context Bundle Assembler Module

This module packages all generated artifacts into a structured context bundle for LLM consumption.
"""

from codex_arch.bundler.context_bundle_assembler import ContextBundleAssembler

# Add BundleAssembler as an alias for ContextBundleAssembler to support backward compatibility
BundleAssembler = ContextBundleAssembler

__all__ = ['ContextBundleAssembler', 'BundleAssembler'] 