#!/usr/bin/env python3
"""
Main entry point for Bibliophile Assistant CLI.
"""

import sys
import os

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bibliophile.cli import main

if __name__ == "__main__":
    main()
