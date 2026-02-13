#!/bin/bash
# SEO Operations Agent - Auto Installer (Unix/Linux/macOS)
# Downloads the latest .skill file from GitHub releases

echo "🚀 SEO Operations Agent Installer"
echo "================================="
echo ""

REPO="0xMoji/seo-operations-agent"
SKILL_FILE="seo-operations-agent.skill"
RELEASE_URL="https://github.com/$REPO/releases/latest/download/$SKILL_FILE"

echo "📦 Downloading latest version from GitHub..."
echo "   URL: $RELEASE_URL"
echo ""

if command -v curl &> /dev/null; then
    curl -L -o "$SKILL_FILE" "$RELEASE_URL"
elif command -v wget &> /dev/null; then
    wget -O "$SKILL_FILE" "$RELEASE_URL"
else
    echo "❌ Error: Neither curl nor wget found"
    echo "   Please install curl or wget to use this installer"
    exit 1
fi

if [ -f "$SKILL_FILE" ]; then
    FILE_SIZE=$(du -h "$SKILL_FILE" | cut -f1)
    echo "✅ Downloaded successfully!"
    echo "   File: $SKILL_FILE ($FILE_SIZE)"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Load $SKILL_FILE into OpenClaw"
    echo "   2. Follow the setup guide in the repository"
    echo ""
    echo "📚 Documentation: https://github.com/$REPO"
else
    echo "❌ Download failed"
    echo ""
    echo "💡 Manual download:"
    echo "   Visit: https://github.com/$REPO/releases/latest"
    exit 1
fi
