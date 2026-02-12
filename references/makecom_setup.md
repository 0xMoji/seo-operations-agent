# Make.com Integration Setup

Complete guide for setting up automated multi-platform content distribution via Make.com and Buffer.

---

## Overview

Make.com acts as the **distribution pipe** in the Brain-Hub-Pipe architecture:
- **Webhook trigger** from OpenClaw when content is ready
- **Airtable query** for approved content marked "Next to Publish"
- **Platform routing** based on Platform field (X Twitter, LinkedIn)  
- **Buffer publishing** to social media channels
- **Status updates** back to Airtable

> [!NOTE]
> The "Website" platform is handled directly by OpenClaw via your website API, not through Make.com.

---

## Quick Start: Import Blueprint

### Option 1: Use Pre-built Blueprint (Recommended)

1. **Download Blueprint**  
   File: `references/makecom_blueprint.json`

2. **Import to Make.com**
   - Log in to [Make.com](https://www.make.com)
   - Create new scenario
   - Click "..." menu → "Import Blueprint"
   - Upload `makecom_blueprint.json`

3. **Replace Placeholders**
   
   The blueprint contains these placeholders you must replace:

   | Placeholder | How to Find It |
   |-------------|----------------|
   | `{{YOUR_WEBHOOK_ID}}` | Created automatically on import, copy webhook URL |
   | `{{YOUR_AIRTABLE_CONNECTION_ID}}` | Click "Add" → Connect Airtable account |
   | `{{YOUR_BASE_ID}}` | From Airtable URL: `airtable.com/appXXXXXXXXXX` |
   | `{{YOUR_CONTENT_HUB_TABLE_ID}}` | Select "Content_Hub" table in Airtable module |
   | `{{YOUR_BUFFER_CONNECTION_ID}}` | Click "Add" → Connect Buffer account |
   | `{{YOUR_TWITTER_PROFILE_ID}}` | Select your X/Twitter profile in Buffer module |
   | `{{YOUR_LINKEDIN_PROFILE_ID}}` | Select your LinkedIn profile in Buffer module |

4. **Test & Activate**
   - Click "Run once" to test
   - Check Airtable and Buffer for results
   - Click "ON" to activate

5. **Configure OpenClaw**
   - Copy the webhook URL from step 3
   - Add to `.env`: `MAKECOM_WEBHOOK_URL=https://hook.us2.make.com/xxxxx`

### Option 2: Manual Setup

Follow the detailed steps below if you prefer to build from scratch.

---

## Manual Setup Instructions

### Step 1: Create New Scenario

1. Log in to [Make.com](https://www.make.com)
2. Click **"Create a new scenario"**
3. Name it: **"SEO Content Distribution"**

### Step 2: Add Webhook Trigger

1. Click **"+"** to add a module
2. Search for **"Webhooks"**
3. Select **"Custom webhook"**
4. Click **"Create a new webhook"**
5. Name it: **"OpenClaw SEO Trigger"**
6. **Copy the webhook URL** - you'll need this for OpenClaw

**Expected Payload** (optional):
```json
{
  "action": "publish",
  "timestamp": "2026-02-12T21:00:00Z"
}
```

### Step 3: Search Approved Content

**Module**: Airtable → Search Records

**Configuration**:
- **Connection**:  Add your Airtable connection (API Key method)
- **Base**: Select "SEO Content Hub"
- **Table**: `Content_Hub`
- **Formula**: `AND({Status}="Approved", {Next to Publish})`
- **Max records**: `10`
- **Fields to output**:
  - Title
  - Body
  - Status
  - Platform
  - Scheduled Time
  - Next to Publish

**What this does**: Fetches all approved content marked for immediate publishing.

### Step 4: Add Router

**Module**: Flow Control → Router

Create 2 routes based on Platform field:

#### Route 1: X (Twitter)

**Filter Condition**:
```
{{Platform}} contains "X (Twitter)"
```

**Actions**:
1. **Buffer → Create Status**
   - Profile: Select Twitter/X profile
   - Text: `{{Body}}`
   - Publication: "Post immediately"
   - Shorten links: Yes

2. **Airtable → Update Record**
   - Record ID: `{{id}}`
   - Fields to update:
     - `Status` = "Published"
     - `Next to Publish` = unchecked
     - `Published At` = `{{now}}`

Don't worry if you have duplicate "Airtable update" modules in multiple routes - Make.com ignores upserts.

#### Route 2: LinkedIn

**Filter Condition**:
```
{{Platform}} contains "LinkedIn"
```

**Actions**:
1. **Buffer → Create Status**
   - Profile: Select LinkedIn profile
   - Text: `{{Body}}`
   - Publication: "Post immediately"
   - Shorten links: Yes

2. **Airtable → Update Record**
   - Record ID: `{{id}}`
   - Fields to update:
     - `Status` = "Published"
     - `Next to Publish` = unchecked
     - `Published At` = `{{now}}`

> [!WARNING]
> Do NOT create a "Website" route. OpenClaw publishes directly to your website API.

---

## Platform Routing Logic

| Platform Field | Distribution Method |
|----------------|---------------------|
| `X (Twitter)` | Make.com → Buffer → Twitter |
| `LinkedIn` | Make.com → Buffer → LinkedIn |
| `Website` | OpenClaw → Your Website API (direct) |

**Example**: If Platform = ["X (Twitter)", "Website"]:
1. Make.com publishes to Twitter via Buffer
2. OpenClaw publishes to your website API
3. Both update Airtable independently

---

## Airtable Filter Formula

The scenario uses this formula to find publishable content:

```
AND({Status}="Approved", {Next to Publish})
```

**Breakdown**:
- `{Status}="Approved"` - Content has been reviewed
- `{Next to Publish}` - Checkbox marking content for immediate publishing

**How it works**:
1. OpenClaw generates content and saves to Airtable
2. When publishing time arrives, OpenClaw sets `Next to Publish = true`
3. OpenClaw triggers Make.com webhook
4. Make.com publishes and unsets the flag

---

## Testing Your Setup

### Test 1: Manual Airtable Trigger

1. In Airtable, create a test record in `Content_Hub`:
   - Title: "Test Post"
   - Body: "This is a test #testing"
   - Status: "Approved"
   - Platform: ["X (Twitter)"]
   - Next to Publish: ✓ (checked)

2. In Make.com, click "Run once"

3. Verify:
   - ✅ Twitter post appears on your profile
   - ✅ Airtable record Status → "Published"
   - ✅ Next to Publish → unchecked

### Test 2: Webhook Trigger

1. Copy your webhook URL from Make.com
2. Send test POST request:
   ```bash
   curl -X POST https://hook.us2.make.com/xxxxxxxxxxxxx
   ```
3. Check execution in Make.com scenario history

### Test 3: Linke dIn Route

1. Update test record: Platform = ["LinkedIn"]
2. Check "Next to Publish" again
3. Run scenario
4. Verify LinkedIn post

---

## Error Handling

Add error handling to Buffer modules:

1. Right-click on Buffer module → **"Add error handler"**
2. Select **"Airtable → Update Record"**
3. Configure:
   - Record ID: `{{id}}`
   - Fields:
     - `Status` = "Failed"
     - `Error Message` = `{{error.message}}`

---

## Common Issues

### "No records found"

**Cause**: Filter formula doesn't match any records

**Fix**:
- Check Status = exactly "Approved" (case-sensitive)
- Check Next to Publish is checked (true)
- View Airtable to confirm matching records exist

### "Buffer authentication failed"

**Cause**: Buffer connection expired

**Fix**:
- Reconnect Buffer in Make.com
- Re-authorize all profiles

### "Content truncated on Twitter"

**Cause**: Body exceeds 280 characters

**Solution**:
- Use OpenClaw's platform-specific content generation
- Twitter content should be generated with 280-char limit automatically

---

## Cost Estimate

**Make.com Free Tier**:
- 1,000 operations/month
- 1 operation = 1 module execution

**Example** (30 articles/month, 2 platforms each):
- Webhook trigger: 30 ops
- Airtable search: 30 ops  
- Buffer publish: 60 ops (2 × 30)
- Airtable update: 60 ops
- **Total**: 180 ops/month ✅ Within free tier

---

## Next Steps

1. ✅ Import Make.com blueprint or build manually
2. Configure OpenClaw webhook URL in `.env`
3. Test with sample content
4. Activate scenario
5. Start your SEO campaign!

For website direct publishing setup, see the implementation plan for Phase 5.
