#!/usr/bin/env python3
"""
Generate winget manifest files for Bibliophile Assistant.

Usage:
    python scripts/generate_winget.py v0.1.1

This reads the latest release assets to get the download URL and SHA256,
then outputs a winget manifest file.
"""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

REPO_OWNER = "JyslaFancy"
REPO_NAME = "Bibliophile-Assistant"
PACKAGE_IDENTIFIER = f"{REPO_OWNER}.{REPO_NAME}"


def sha256_url(url: str) -> str:
    """Download a URL and return its SHA256 hex digest."""
    print(f"  Downloading {url} to compute hash...")
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
    h = hashlib.sha256(data).hexdigest()
    print(f"  SHA256: {h}")
    return h


def get_release_assets(tag: str) -> list:
    """Fetch release assets from GitHub API."""
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{tag}"
    print(f"  Fetching release: {api_url}")
    req = urllib.request.Request(api_url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")

    with urllib.request.urlopen(req) as resp:
        release = json.loads(resp.read())

    return release.get("assets", [])


def make_installer_manifest(tag: str, url: str, sha256: str, installer_type: str) -> dict:
    """Generate a winget installer manifest."""
    version = tag.lstrip("v")

    return {
        "PackageIdentifier": PACKAGE_IDENTIFIER,
        "PackageVersion": version,
        "DefaultLocale": "en-US",
        "ManifestType": "version",
        "ManifestVersion": "1.6.0",
        "Installers": [
            {
                "Architecture": "x64",
                "InstallerType": installer_type,
                "InstallerUrl": url,
                "InstallerSha256": sha256,
                "Commands": ["bibliophile"],
                "Scope": "user",
            }
        ],
    }


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: python scripts/generate_winget.py <version-tag>")
        print("Example: python scripts/generate_winget.py v0.1.1")
        sys.exit(1)

    tag = argv[0]
    version = tag.lstrip("v")

    print(f"Generating winget manifest for {tag}")
    print()

    # This gets the Windows artifact from our GitHub release
    # The filename comes from our build workflow
    exe_filename = f"bibliophile.exe"
    download_url = (
        f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        f"/releases/download/{tag}/{exe_filename}"
    )

    # Compute SHA256 from the release URL
    sha = sha256_url(download_url)

    # Build manifest for portable installer
    manifest = make_installer_manifest(tag, download_url, sha, "portable")

    # Write manifest
    import yaml

    output = yaml.dump(manifest, sort_keys=False, default_flow_style=False, allow_unicode=True)
    print()
    print("=" * 60)
    print(output)
    print("=" * 60)
    print()

    # Also write to file
    out_dir = Path("winget")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"{PACKAGE_IDENTIFIER}.installer.yaml"
    out_file.write_text(output)
    print(f"Manifest written to: {out_file}")
    print()
    print("Next steps:")
    print(f"  1. Fork https://github.com/microsoft/winget-pkgs")
    print(f"  2. Copy manifests/ into the winget-pkgs repo under:")
    print(f"     manifests/{PACKAGE_IDENTIFIER[0].lower()}/{PACKAGE_IDENTIFIER.replace('.', '/')}/{version}/")
    print(f"  3. Submit a PR to winget-pkgs")
    print()
    print("  After merge, users can run:")
    print(f"    winget install {REPO_OWNER}.{REPO_NAME}")


if __name__ == "__main__":
    main()
