#!/usr/bin/env python3
"""
Setup script for Bibliophile Assistant.
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [
        line.strip() for line in f.read().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="bibliophile-assistant",
    version="0.1.0",
    description="Document-based AI assistant using Ollama and ChromaDB",
    author="Harald Daltveit",
    author_email="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bibliophile=bibliophile.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
