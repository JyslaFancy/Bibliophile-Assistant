# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Bibliophile Assistant.
Builds a single standalone executable with all dependencies bundled.

Usage:
    pip install pyinstaller
    pyinstaller bibliophile.spec
"""

import sys
import os
from pathlib import Path

# Add repo root to path so we can import the package
repo_root = Path(SPECPATH).parent
sys.path.insert(0, str(repo_root / "src"))

# Auto-collect all submodules of packages prone to dynamic imports
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect all hidden imports needed for the various dependencies
hidden_imports = [
    # Click and Rich (CLI framework)
    "click",
    "rich",
    "rich.console", "rich.panel", "rich.progress",
    "rich.table", "rich.text", "rich.markup",

    # ChromaDB — collect all submodules to catch dynamic imports
    *collect_submodules("chromadb"),
    # Sentence-transformers / HuggingFace (used by ChromaDB's default embedding)
    *collect_submodules("tokenizers"),
    "onnxruntime", "onnxruntime.capi",
    "sqlite3",
    "numpy",
    "numpy.core._methods", "numpy.lib.format",
    "tqdm",
    "yaml",  # PyYAML
    "pydantic", "pydantic.deprecated.decorator",
    "uvicorn", "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
    "uvicorn.protocols", "uvicorn.protocols.http",
    "uvicorn.lifespan", "uvicorn.lifespan.on",
    "starlette", "starlette.routing",
    "fastapi",
    "typing_extensions",
    "overrides",

    # Document processing
    "pypdf", "pypdf.generic",
    "docx",  # python-docx
    "docx.opc", "docx.opc.constants", "docx.oxml",
    "openpyxl",
    "pptx",

    # System utilities
    "psutil",
    "GPUtil",
    "requests",
    "certifi",
    "urllib3",
    "charset_normalizer",
    "idna",

    # Data files
    "json",
    "hashlib",
    "re",
    "platform",
    "subprocess",
    "time",
    "os",
]

a = Analysis(
    ["src/bibliophile/main.py"],
    pathex=[str(repo_root / "src")],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "unittest", "test", "tests",
        "matplotlib", "pandas", "scipy", "PIL",
        "jedi", "ipython", "jupyter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="bibliophile",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
