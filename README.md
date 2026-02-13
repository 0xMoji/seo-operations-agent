# SEO Operations Agent

> **Latest Version**: [Download v2.3.0](https://github.com/0xMoji/seo-operations-agent/releases/latest/download/seo-operations-agent.skill) | [All Releases](https://github.com/0xMoji/seo-operations-agent/releases)

A fully automated, private SEO content generation and distribution system built as an OpenClaw skill.

## Features

- 🧠 **Smart Content Generation**: AI-powered SEO-optimized articles
- 💡 **Knowledge Injection (v2.1)**: Automatically collects your expertise before writing
- 🎨 **Flexible Image Generation (v2.2)**: Support for 8+ AI providers (OpenAI, Google, etc.)
- 📊 **Auto-Tracking (v2.3)**: Keywords Used & Words Count auto-populated
- 📅 **Automated Scheduling**: Set-and-forget content calendar
- 🔔 **Intelligent Reminders**: Pre-publish notifications
- 🌐 **Multi-Platform Distribution**: Custom websites + social media
- 🔒 **Full Privacy**: All data in your Airtable
- 💰 **BYOK Model**: You control all API costs (~$3-5/month)

## Quick Start

1. **Install**: Load the skill into OpenClaw
2. **Configure Airtable**: Add API token to `.env`
3. **Auto-Setup**: Skill creates base and tables automatically
4. **Start Campaign**: `启动一个为期 30 天的计划，主题是 Web3 隐私技术，每天 1 篇`

See [SKILL.md](SKILL.md) for complete documentation.

## Architecture

```
OpenClaw (Scheduler) → Airtable (Hub) → Make.com (Pipe) → Websites + Social
```

**Brain-Hub-Pipe Model**:
- **Brain**: OpenClaw skill (AI content generation, scheduling)
- **Hub**: Airtable (content management, review workflow)
- **Pipe**: Make.com (multi-platform distribution)

## Installation

### Option 1: Auto-Download (Recommended)

**Windows (PowerShell)**:
```powershell
irm https://raw.githubusercontent.com/0xMoji/seo-operations-agent/main/install.ps1 | iex
```

**Unix/Linux/macOS**:
```bash
curl -fsSL https://raw.githubusercontent.com/0xMoji/seo-operations-agent/main/install.sh | bash
```

### Option 2: Manual Download

Download the latest `.skill` file from [Releases](https://github.com/0xMoji/seo-operations-agent/releases/latest) and load into OpenClaw.

### Option 3: Clone Repository

```bash
git clone https://github.com/0xMoji/seo-operations-agent.git
cd seo-operations-agent
# Then run the install script to get the packaged .skill file
./install.sh  # or install.ps1 on Windows
```

Configure environment:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Minimal setup requires just an Airtable API token:

```bash
AIRTABLE_API_KEY=patXXXXXXXXXXXXXX
```

The skill auto-creates the base and tables. See [references/configuration.md](references/configuration.md) for details.

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[Setup Guide](references/setup_guide.md)** - Installation instructions
- **[Make.com Setup](references/makecom_setup.md)** - Distribution automation
- **[Airtable Schema](references/airtable_schema.md)** - Database structure

## Requirements

- **Airtable** (Free tier: 1,200 records)
- **Make.com** (Free tier: 1,000 ops/month)
- **OpenAI API** (Pre-configured in OpenClaw)
- **Unsplash API** (Optional, for images)

## Cost Estimate

Based on 30 articles/month:
- OpenAI GPT-4: ~$3-5
- Others: Free tier sufficient
- **Total: $3-5/month**

## File Structure

```
seo-agent/
├── SKILL.md              # Main documentation
├── scripts/              # Python implementation
│   ├── skill.py
│   ├── airtable_client.py
│   ├── content_engine.py
│   ├── scheduler.py
│   └── intent_parser.py
└── references/           # Additional documentation
    ├── setup_guide.md
    ├── makecom_setup.md
    ├── airtable_schema.md
    └── configuration.md
```

## Usage Examples

```bash
# Create campaign
Start a 30-day campaign on Web3 privacy tech, 1 article per day

# Add keywords
Add these keywords to the pool: zkProof, zero-knowledge proofs, Web3 identity

# Generate content
Generate content now

# Check progress
Report current campaign progress
```

## Privacy & Security

- ✅ No centralized server
- ✅ Data only in your Airtable
- ✅ You own all API keys
- ✅ Full audit trail

## License

MIT License - Use freely in your projects.

## Contributing

Contributions welcome! This skill follows [Anthropic's skill-creator best practices](https://github.com/anthropics/skills/tree/main/skills/skill-creator).

## Support

For issues or questions, see the documentation in the `references/` directory or open a GitHub issue.
