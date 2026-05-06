#!/usr/bin/env python3
"""
Build script for Bibliophile Assistant standalone executable.

Usage:
    python scripts/build.py          # build for current platform
    python scripts/build.py --clean  # clean and rebuild

Produces:
    dist/bibliophile       (Linux/macOS)
    dist/bibliophile.exe   (Windows)
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = REPO_ROOT / "bibliophile.spec"
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"


def run(cmd, **kwargs):
    """Run a command and print output in real time."""
    print(f"\n  RUN: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(REPO_ROOT), **kwargs)


def clean():
    """Remove previous build artifacts."""
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            print(f"  Cleaning {d}...")
            shutil.rmtree(d)

    # Remove PyInstaller .spec build files
    for pat in ["*.spec.bak"]:
        for f in REPO_ROOT.glob(pat):
            f.unlink()
            print(f"  Removed {f}")


def build():
    """Build the standalone executable."""
    # Ensure pyinstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("ERROR: PyInstaller not found. Install with: pip install pyinstaller")
        print("   or: pip install -e '.[dev]'")
        sys.exit(1)

    print("=" * 60)
    print("  Building Bibliophile Assistant")
    print("=" * 60)

    # Build with PyInstaller
    result = run(
        [sys.executable, "-m", "PyInstaller", str(SPEC_FILE),
         "--noconfirm", "--distpath", str(DIST_DIR),
         "--workpath", str(BUILD_DIR)],
    )

    if result.returncode != 0:
        print("\n  BUILD FAILED!")
        sys.exit(result.returncode)

    print("\n" + "=" * 60)
    print("  BUILD SUCCESSFUL!")
    print("=" * 60)

    # Show the output
    exe_names = ["bibliophile.exe", "bibliophile"]
    for name in exe_names:
        path = DIST_DIR / name
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  Output: {path}")
            print(f"  Size:   {size_mb:.1f} MB")
            break


def main():
    args = sys.argv[1:]

    if "--clean" in args or "-c" in args:
        clean()

    if "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    build()


if __name__ == "__main__":
    main()
