# Make.com Scenario Setup Guide

This guide will walk you through creating the Make.com automation scenario for multi-platform content distribution.

## Prerequisites

- Make.com account (free tier sufficient)
- Your Airtable Base ID and API key
- Buffer account (if using social media distribution)

## Step 1: Create New Scenario

1. Log in to [Make.com](https://www.make.com)
2. Click **"Create a new scenario"**
3. Name it: **"SEO Agent - Content Distribution"**

## Step 2: Add Webhook Trigger

1. Click **"+"** to add a module
2. Search for **"Webhooks"**
3. Select **"Custom webhook"**
4. Click **"Create a new webhook"**
5. Name it: **"SEO Content Trigger"**
6. **Copy the webhook URL** - you'll need this for your `.env` file

**Expected Payload**:
```json
{
  "action": "publish",
  "timestamp": "2026-02-10T21:00:00Z"
}
```

## Step 3: Search Approved Content

1. Add module: **Airtable → Search Records**
2. Configure:
   - **Connection**: Add your Airtable connection
     - API Key: From `.env` file
   - **Base**: Select your SEO base
   - **Table**: `Content_Hub`
   - **Formula**: `{Status} = "已批准"`
   - **Max records**: `50`

## Step 4: Add Iterator

1. Add module: **Flow Control → Iterator**
2. **Array**: Map to `{{1.records}}`

This will process each approved article individually.

## Step 5: Router for Multi-Platform Distribution

1. Add module: **Flow Control → Router**

### Route 1: Custom Website Publishing

**Filter**: `{{2.website_webhook_url}}` exists

**Module**: HTTP → Make a Request
- **URL**: `{{2.website_webhook_url}}`
- **Method**: POST
- **Body type**: Raw
- **Content type**: JSON
- **Request content**:
  ```json
  {
    "title": "{{2.Title}}",
    "body": "{{2.Body}}",
    "slug": "{{2.SEO Metadata.slug}}",
    "meta_description": "{{2.SEO Metadata.description}}",
    "featured_image": "{{first(2.Cover Image).url}}",
    "published_at": "{{now}}"
  }
  ```

**Headers** (if API key required):
```
Authorization: Bearer YOUR_WEBSITE_API_TOKEN
```

**Save response** to variable `websiteResponse`

### Route 2: Buffer Social Media

**Filter**: `{{2.Buffer Channels}}` is not empty

**Iterator**: Loop through `{{2.Buffer Channels}}`

**Module**: Buffer → Create Post
- **Profile**: Map channel to Buffer profile ID
  - twitter → your Twitter profile ID
  - linkedin → your LinkedIn profile ID
- **Text**: `{{2.Social Snippet}}`
- **Media**: `{{first(2.Cover Image).url}}`

## Step 6: Update Airtable Status

After the router, add:

**Module**: Airtable → Update Record
- **Record ID**: `{{2.id}}`
- **Fields**:
  - `Status`: `已发布`
  - `Live URL`: `{{websiteResponse.data.url}}`
  - `Published At`: `{{now}}`

## Step 7: Error Handling

Add error handler to Route 1:

1. Right-click on HTTP module → **"Add error handler"**
2. Select **"Airtable → Update Record"**
3. Configure:
   - **Record ID**: `{{2.id}}`
   - **Fields**:
     - `Status`: `发布失败`
     - `Error Message`: `{{error.message}}`

## Step 8: Test the Scenario

1. Click **"Run once"**
2. From OpenClaw, run: `trigger_publish`
3. Check Make.com execution log
4. Verify content appears on your website and social media

## Step 9: Activate Scenario

1. Toggle **"Scheduling"** to ON
2. Set to **"Immediately as data arrives"**
3. Click **"OK"**

Your scenario is now live!

## Configuration Summary

**Environment Variables to Set**:
```bash
MAKECOM_WEBHOOK_URL=https://hook.eu1.make.com/YOUR_WEBHOOK_ID
```

## Scenario Template (JSON)

For quick setup, import this template:

<details>
<summary>Click to expand template JSON</summary>

```json
{
  "name": "SEO Agent - Content Distribution",
  "flow": [
    {
      "id": 1,
      "module": "gateway:CustomWebHook",
      "parameters": {
        "hook": "seo_content_trigger"
      }
    },
    {
      "id": 2,
      "module": "airtable:searchRecords",
      "parameters": {
        "base": "{{YOUR_BASE_ID}}",
        "table": "Content_Hub",
        "formula": "{Status} = \"已批准\"",
        "maxRecords": 50
      }
    },
    {
      "id": 3,
      "module": "builtin:Iterator",
      "parameters": {
        "array": "{{2.records}}"
      }
    },
    {
      "id": 4,
      "module": "builtin:Router",
      "routes": [
        {
          "flow": [
            {
              "id": 5,
              "module": "http:makeRequest",
              "filter": {
                "name": "Has website webhook",
                "conditions": [
                  {
                    "a": "{{3.website_webhook_url}}",
                    "o": "exists"
                  }
                ]
              }
            }
          ]
        },
        {
          "flow": [
            {
              "id": 6,
              "module": "buffer:createPost"
            }
          ]
        }
      ]
    },
    {
      "id": 7,
      "module": "airtable:updateRecord",
      "parameters": {
        "base": "{{YOUR_BASE_ID}}",
        "table": "Content_Hub",
        "recordId": "{{3.id}}"
      }
    }
  ]
}
```

</details>

## Troubleshooting

### Webhook not triggering
- Check that `MAKECOM_WEBHOOK_URL` is set correctly in `.env`
- Verify scenario is **active** (scheduling ON)
- Check Make.com execution history for errors

### Airtable connection fails
- Verify API key has `data.records:read` and `data.records:write` permissions
- Check Base ID is correct

### Buffer posts not creating
- Ensure Buffer account is connected in Make.com
- Verify profile IDs are correct
- Check Buffer free tier limits (10 scheduled posts/channel)

## Cost Estimate

- **Make.com Free Tier**: 1,000 operations/month
- **Per article**: ~5-7 operations
- **Capacity**: ~140-200 articles/month on free tier

For higher volumes, upgrade to Make.com Pro ($9/month = 10,000 operations).

## Next Steps

After setup:
1. Copy webhook URL to your `.env` file
2. Restart the OpenClaw skill
3. Test with: `trigger_publish`

