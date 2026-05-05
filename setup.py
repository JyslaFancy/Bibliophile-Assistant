#!/usr/bin/env python3
"""
Setup script for Bibliophile Assistant.
"""

import os
from setuptools import setup, find_packages
from pathlib import Path

# Get the directory where setup.py is located
here = Path(__file__).parent.resolve()

# Read requirements
requirements_path = here / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [
            line.strip() for line in f.read().splitlines()
            if line.strip() and not line.startswith("#")
        ]

# Read long description from README
readme_path = here / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="bibliophile-assistant",
    version="0.1.0",
    description="Document-based AI assistant using Ollama and ChromaDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Harald Daltveit",
    author_email="harald@daltveit.com",
    url="https://github.com/JyslaFancy/Bibliophile-Assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bibliophile=bibliophile.main:main",
        ],
    },
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
)
