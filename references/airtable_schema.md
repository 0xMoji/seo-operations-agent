# Airtable Schema Reference

Complete schema definition for the SEO Content Hub Airtable base (v2.0).

## Campaign_Settings

Campaign configuration and scheduling settings.

| Field Name | Type | Description |
|------------|------|-------------|
| `Plan Name` | Single line text | Campaign identifier |
| `Start Date` | Date | Campaign start date |
| `End Date` | Date | Campaign end date |
| `Frequency` | Number | Posts per day (integer) |
| `Publish Time` | Single line text | Daily publish time (format: "HH:MM", e.g., "10:00") |
| `Website Webhook URL` | URL | Optional custom website API endpoint for publishing |
| `Buffer Channels` | Multiple select | Social media channels (options: twitter, linkedin, bluesky) |
| `Auto Approve` | Checkbox | Skip manual review if enabled |
| `Is Active` | Checkbox | Campaign status (active/inactive) |

## Keyword_Pool

Keyword library for content generation.

| Field Name | Type | Description |
|------------|------|-------------|
| `Keyword` | Single line text | Search term or topic keyword |
| `Status` | Single select | Usage status (options: **Available**, **Used**, **Deprecated**) |

## Content_Hub

Generated content library with multi-platform publishing workflow.

| Field Name | Type | Description |
|------------|------|-------------|
| `Title` | Single line text | Article title |
| `Body` | Long text | Full content (HTML for website, plain text for social) |
| `SEO Metadata` | Long text | JSON containing: slug, description, schema_markup |
| `Social Snippet` | Long text | Social media post text (< 280 characters) |
| `Images` | Multiple Attachments | All images for this content (cover + inline) |
| `Image Metadata` | Long text | JSON array with image positions and purposes (see below) |
| `Status` | Single select | Workflow status (options: **Pending**, **Approved**, **Publishing**, **Published**, **Failed**) |
| `Platform` | Multiple select | Distribution channels (options: **X (Twitter)**, **LinkedIn**, **Website**) |
| `Scheduled Time` | Date & Time | When to publish this content |
| `Next to Publish` | Checkbox | Flag for Make.com to pick up for immediate publishing |
| `Live URL` | URL | Published article URL (filled by Make.com after publishing) |
| `Published At` | Date & Time | Publication timestamp (filled by Make.com) |

### Image Metadata JSON Structure

The `Image Metadata` field contains an array mapping images to their usage:

```json
[
  {
    "filename": "cover-image.jpg",
    "purpose": "cover",
    "platforms": ["Website", "LinkedIn", "X (Twitter)"],
    "position": "featured",
    "alt_text": "Descriptive alt text for accessibility",
    "source": "dall-e-3"
  },
  {
    "filename": "inline-diagram.png",
    "purpose": "inline",
    "platforms": ["Website"],
    "position": "after-paragraph-2",
    "alt_text": "Workflow diagram showing SEO process",
    "source": "unsplash"
  },
  {
    "filename": "social-thumbnail.jpg",
    "purpose": "social",
    "platforms": ["X (Twitter)", "LinkedIn"],
    "position": "attached",
    "alt_text": "Eye-catching social media thumbnail",
    "source": "manual"
  }
]
```

**Field Definitions**:
- `filename`: Matches the attachment filename in the `Images` field
- `purpose`: `cover` | `inline` | `social` | `thumbnail`
- `platforms`: Array of platforms where this image is used
- `position`: 
  - `featured` - Hero/cover image at top
  - `after-paragraph-N` - Inline after specific paragraph (Website only)
  - `attached` - Attached to post (X, LinkedIn)
  - `end` - At the end of content
- `alt_text`: Accessibility description
- `source`: `dall-e-3` | `unsplash` | `manual` | `user-upload`

## Platform Field Options

The `Platform` field is a multi-select that determines distribution channels:

- **X (Twitter)**: Published via Make.com → Buffer → Twitter/X
- **LinkedIn**: Published via Make.com → Buffer → LinkedIn
- **Website**: Published directly by OpenClaw via your website API

**Example**: If Platform = ["X (Twitter)", "Website"], the content will:
1. Post to Twitter via Make.com automation
2. Post to your website via OpenClaw direct API call

## SEO Metadata JSON Structure

The `seo_metadata` field contains a JSON object:

```json
{
  "slug": "url-friendly-article-slug",
  "description": "SEO meta description (150-160 characters)",
  "schema_markup": {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Article Title",
    "description": "Meta description",
    "author": {
      "@type": "Organization",
      "name": "Your Organization"
    },
    "datePublished": "2026-02-12T10:00:00Z",
    "keywords": "keyword1, keyword2"
  }
}
```

## Status Workflow

Content status follows this workflow:

```
Pending
    ↓
Approved ← Manual user action in Airtable
    ↓
Published ← Set by Make.com after successful publish
```

**Status Definitions**:
- **Pending**: Newly generated content awaiting review
- **Approved**: Reviewed and ready for publishing
- **Published**: Successfully published to platform(s)

## Publishing Workflow

The `Next to Publish` checkbox controls when Make.com publishes content:

1. **Content Generation**: OpenClaw creates content with Status = "Pending" or "Approved"
2. **Scheduling**: Content sits in Airtable with `Scheduled Time` set
3. **Trigger Time**: When OpenClaw's scheduler hits `Scheduled Time`:
   - Sets `Next to Publish = true` on that record
   - Triggers Make.com webhook
4. **Make.com Execution**: 
   - Queries Airtable: `AND({Status}="Approved", {Next to Publish})`
   - Publishes to platforms based on `Platform` field
   - Updates Status = "Published", Next to Publish = false

## Auto-Creation

When using the skill's auto-initialization feature (`check_and_initialize_base()`), all three tables are created automatically with the correct field types and select options. No manual table creation is required.

**Required Airtable API Permissions**:
- `schema.bases:read` - Read base structure
- `schema.bases:write` - Create bases and tables
- `data.records:read` - Read content
- `data.records:write` - Update status
