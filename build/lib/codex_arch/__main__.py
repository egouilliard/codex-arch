#!/usr/bin/env python
"""
Main entry point for the codex-arch package.
This allows running the package with `python -m codex_arch`
"""

import sys
from codex_arch.cli.main import main

if __name__ == "__main__":
    sys.exit(main()) 