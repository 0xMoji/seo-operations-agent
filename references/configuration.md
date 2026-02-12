# Configuration Reference

Environment variables and configuration details for the SEO Operations Agent.

## Required Environment Variables

Create a `.env` file in the skill directory with the following variables:

### Airtable Configuration

```bash
# Airtable API Token
# Get from: https://airtable.com/create/tokens
# Required permissions: data.records:read, data.records:write, schema.bases:read, schema.bases:write
AIRTABLE_API_KEY=patXXXXXXXXXXXXXX

# Base ID (auto-generated during setup, or manually specified)
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX

# Table and View IDs (optional, defaults work for auto-created bases)
AIRTABLE_CONTENT_TABLE_ID=tblContentHub
AIRTABLE_GRID_VIEW_ID=viwGridView
```

### OpenAI Configuration

```bash
# OpenAI API Key (pre-configured in OpenClaw)
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXX
```

### Optional Services

```bash
# Unsplash (for royalty-free images)
# Get from: https://unsplash.com/developers
UNSPLASH_ACCESS_KEY=XXXXXXXXXXXXXXXX

# Make.com (for automated distribution)
# Get from: Make.com scenario webhook settings
MAKECOM_WEBHOOK_URL=https://hook.eu1.make.com/XXXXXXXXXXXXXXXX
```

## Setup Process

1. **Copy template**:
   ```bash
   cp .env.example .env
   ```

2. **Add Airtable API token** (minimum required)

3. **Run skill** - Base will be auto-created if not configured

4. **Restart skill** after base creation to use new `AIRTABLE_BASE_ID`

## Configuration Validation

The skill validates configuration during startup:

- ✅ `AIRTABLE_API_KEY` is set
- ✅ API key has required permissions
- ✅ Base exists or can be created
- ⚠️ Make.com webhook URL (optional, needed for auto-publishing)
- ⚠️ Unsplash API key (optional, for automatic images)

## Detailed Setup Guides

- **Complete setup**: See [setup_guide.md](./setup_guide.md)
- **Make.com integration**: See [makecom_setup.md](./makecom_setup.md)
- **Auto-initialization**: See [auto_init_example.md](./auto_init_example.md)

## Service Tier Requirements

| Service | Free Tier | What's Needed |
|---------|-----------|---------------|
| Airtable | 1,200 records/base | ~100-300 records for typical campaign |
| Make.com | 1,000 operations/month | ~5-7 ops per article = 140-200 articles/month |
| OpenAI | Pay-as-you-go | ~$3-5/month for 30 articles |
| Unsplash | 50 requests/hour | 30 requests/month typically |

Free tiers are sufficient for typical usage (30-50 articles/month).
