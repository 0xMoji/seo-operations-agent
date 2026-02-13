# Installation Guide for AI Agents

## ⚠️ IMPORTANT: This is a Pre-Packaged Skill

This repository contains **source code** for development. If you cloned this repository, you are in the **wrong place** for installation.

## What You Need

You need the **pre-built `.skill` file**, not the source code.

## How to Get the Skill File

### Option 1: Direct Download (Recommended)

Run this command to download the latest release:

```bash
curl -L -o seo-operations-agent.skill \
  https://github.com/0xMoji/seo-operations-agent/releases/latest/download/seo-operations-agent.skill
```

### Option 2: Using Git Tags

If you need to verify the version:

```bash
# Get latest version tag
LATEST_TAG=$(git ls-remote --tags https://github.com/0xMoji/seo-operations-agent.git | \
  grep -o 'refs/tags/v[0-9.]*$' | sort -V | tail -1 | sed 's/refs\/tags\///')

echo "Latest version: $LATEST_TAG"

# Download that version
curl -L -o seo-operations-agent.skill \
  "https://github.com/0xMoji/seo-operations-agent/releases/download/$LATEST_TAG/seo-operations-agent.skill"
```

### Option 3: Build from Source (Only if you need to modify the code)

If you cloned this repo and want to package it yourself:

```bash
# You are already in the cloned directory
python -m zipfile -c seo-operations-agent.skill SKILL.md README.md .env.example requirements.txt scripts/ references/
```

## Next Steps

Once you have `seo-operations-agent.skill`:

1. Load it into OpenClaw
2. The skill will guide you through Airtable setup on first run
3. Start generating content with natural language commands

## Current Version

Latest: **v2.3.0**

## What's in This Version

- v2.3: Auto-populated Keywords Used & Words Count
- v2.2: Flexible image generation (8+ providers)
- v2.1: Automated knowledge injection
- Full SEO content automation with Airtable + Make.com

## Documentation

After obtaining the skill file, refer to `SKILL.md` inside the package for complete documentation.
