#!/usr/bin/env python3
"""
Setup script for Bibliophile Assistant.
Reads version from bibliophile/__init__.py so there's a single source of truth.
"""

from setuptools import setup
import re
from pathlib import Path

def get_version():
    """Read version from src/bibliophile/__init__.py."""
    init = Path(__file__).resolve().parent / "src" / "bibliophile" / "__init__.py"
    content = init.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    raise RuntimeError("Version not found in __init__.py")

setup(version=get_version())
