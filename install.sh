#!/usr/bin/env bash
# Bibliophile Assistant — Linux Installer
# One-liner: curl -fsSL https://raw.githubusercontent.com/JyslaFancy/Bibliophile-Assistant/main/install.sh | bash
#
# Downloads the latest bibliophile binary to ~/.local/bin/

set -euo pipefail

REPO="JyslaFancy/Bibliophile-Assistant"
VERSION="${1:-latest}"
INSTALL_DIR="${HOME}/.local/bin"

echo ""
echo "    Bibliophile Assistant Installer"
echo "    ==============================="
echo ""

# --- Determine download URL ---
if [ "$VERSION" = "latest" ]; then
    echo "  Finding latest release..."
    TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    if [ -z "$TAG" ]; then
        echo "  ERROR: Could not find latest release. Try specifying a version:"
        echo "    curl .../install.sh | bash -s v0.1.1"
        exit 1
    fi
else
    TAG="$VERSION"
    [[ "$TAG" != v* ]] && TAG="v$TAG"
fi

URL="https://github.com/${REPO}/releases/download/${TAG}/bibliophile"
echo "  Version: $TAG"
echo "  Download: $URL"

# --- Download ---
mkdir -p "$INSTALL_DIR"
echo "  Downloading..."
if command -v curl &>/dev/null; then
    curl -fsSL "$URL" -o "${INSTALL_DIR}/bibliophile"
else
    wget -q "$URL" -O "${INSTALL_DIR}/bibliophile"
fi

chmod +x "${INSTALL_DIR}/bibliophile"
echo "  Installed: ${INSTALL_DIR}/bibliophile"

# --- Check PATH ---
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "  Add to PATH (add this to ~/.bashrc or ~/.zshrc):"
    echo "    export PATH=\"\$PATH:${INSTALL_DIR}\""
    echo ""
    echo "  Or for this session:"
    echo "    export PATH=\"\$PATH:${INSTALL_DIR}\""
fi

echo ""
echo "  DONE! Run 'bibliophile setup' to get started."
echo ""
