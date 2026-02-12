# Simplified Setup Guide (Auto-Initialization)

With automatic base creation, setup is now much simpler!

## Quick Setup (3 Steps)

### Step 1: Get Airtable API Token

1. Go to [Airtable Tokens](https://airtable.com/create/tokens)
2. Click **"Create new token"**
3. Name: **"SEO Agent"**
4. Add these permissions:
   - ✅ `data.records:read`
   - ✅ `data.records:write`
   - ✅ `schema.bases:read`
   - ✅ `schema.bases:write`
5. **Copy the token** (starts with `pat...`)

### Step 2: Configure Skill

1. Copy `.env.example` to `.env`:
   ```bash
   cd e:\Code\openclaw-skills\seo-agent
   cp .env.example .env
   ```

2. Edit `.env` and add your Airtable token:
   ```bash
   AIRTABLE_API_KEY=pat_YOUR_TOKEN_HERE
   OPENAI_API_KEY=sk-YOUR_KEY_HERE
   ```

3. Start the skill:
   ```bash
   python skill.py
   ```

### Step 3: Initialize System

In OpenClaw conversation, say:

```
我想启动 SEO 自动化
```

The system will:
1. ✅ Check your Airtable API permissions
2. ✅ Automatically create a new base: **"SEO Content Hub"**
3. ✅ Create all 3 tables with proper schema
4. ✅ Save the base ID to your `.env` file
5. ✅ Give you a direct link to the new base

**That's it!** No manual table creation needed.

---

## What Gets Created Automatically

### Base: "SEO Content Hub"

#### Table 1: Campaign_Settings
| Field | Type | Purpose |
|-------|------|---------|
| Plan Name | Text | Campaign identifier |
| Start Date | Date | Campaign start |
| End Date | Date | Campaign end |
| Frequency | Number | Posts per day |
| Publish Time | Text | Daily publish time (HH:MM) |
| Auto Approve | Checkbox | Skip manual review |
| Is Active | Checkbox | Campaign status |
| Website Webhook URL | URL | Custom site API endpoint |
| Buffer Channels | Multi-select | twitter/linkedin/bluesky |

#### Table 2: Keyword_Pool
| Field | Type | Purpose |
|-------|------|---------|
| Keyword | Text | Search term |
| Category | Select | General/Technical/Business |
| Status | Select | 未开始/已使用/失效 |

#### Table 3: Content_Hub
| Field | Type | Purpose |
|-------|------|---------|
| Title | Text | Article title |
| Body | Long text | Full HTML content |
| SEO Metadata | Long text | JSON: slug, description, schema |
| Social Snippet | Long text | Twitter/LinkedIn snippet |
| Cover Image | Attachment | Featured image |
| Status | Select | 待审核/已批准/发布中/已发布/发布失败 |
| Live URL | URL | Published article URL |
| Published At | DateTime | Publish timestamp |
| Error Message | Long text | Failure details |

---

## Optional Configuration

### Unsplash (For Images)
```bash
# Add to .env
UNSPLASH_ACCESS_KEY=your_access_key
```

### Make.com (For Distribution)
Follow [makecom_setup.md](./makecom_setup.md) and add webhook URL:
```bash
# Add to .env
MAKECOM_WEBHOOK_URL=https://hook.eu1.make.com/xxx
```

---

## Troubleshooting

### "Permission Denied"
Make sure your Airtable token has all 4 required scopes:
- data.records:read
- data.records:write
- schema.bases:read ← **Required for auto-creation**
- schema.bases:write ← **Required for auto-creation**

### "Base Already Exists"
If you already have a base:
1. Copy its Base ID from the URL
2. Add to `.env`:
   ```bash
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   ```
3. Re-run setup - it will check and create missing tables only

### Manual Setup (If Needed)
If auto-creation fails, see [setup_guide_manual.md](./setup_guide_manual.md) for step-by-step manual instructions.

---

## Next Steps

After initialization:
1. Create your first campaign
2. Add keywords to the pool
3. Generate content
4. Review in Airtable
5. Publish!

See [SKILL.md](../SKILL.md) for usage examples.
