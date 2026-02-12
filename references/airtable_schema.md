# Airtable Schema Reference

Complete schema definition for the SEO Content Hub Airtable base.

## Campaign_Settings

Campaign configuration and scheduling settings.

| Field Name | Type | Description |
|------------|------|-------------|
| `plan_name` | Single line text | Campaign identifier |
| `start_date` | Date | Campaign start date |
| `end_date` | Date | Campaign end date |
| `frequency` | Number | Posts per day (integer) |
| `publish_time` | Single line text | Daily publish time (format: "HH:MM", e.g., "10:00") |
| `website_webhook_url` | URL | Optional custom website API endpoint for publishing |
| `buffer_channels` | Multiple select | Social media channels (options: twitter, linkedin, bluesky) |
| `auto_approve` | Checkbox | Skip manual review if enabled |
| `is_active` | Checkbox | Campaign status (active/inactive) |

## Keyword_Pool

Keyword library for content generation.

| Field Name | Type | Description |
|------------|------|-------------|
| `keyword` | Single line text | Search term or topic keyword |
| `category` | Single select | Keyword categorization (options: General, Technical, Business) |
| `status` | Single select | Usage status (options: 未开始, 已使用, 失效) |

## Content_Hub

Generated content library with publishing workflow.

| Field Name | Type | Description |
|------------|------|-------------|
| `title` | Single line text | Article title |
| `body` | Long text | Full HTML content |
| `seo_metadata` | Long text | JSON containing: slug, description, schema_markup |
| `social_snippet` | Long text | Social media post text (< 280 characters) |
| `cover_image` | Attachment | Featured image (from Unsplash or DALL-E) |
| `status` | Single select | Workflow status (options: 待审核, 已批准, 发布中, 已发布, 发布失败) |
| `live_url` | URL | Published article URL (filled after publishing) |
| `published_at` | Date & Time | Publication timestamp |
| `error_message` | Long text | Error details if publishing fails |

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
    "datePublished": "2026-02-11T10:00:00Z",
    "keywords": "keyword1, keyword2"
  }
}
```

## Status Workflow

Content status follows this workflow:

```
待审核 (Pending Review)
    ↓
已批准 (Approved) ← Manual user action in Airtable
    ↓
发布中 (Publishing) ← Make.com processing
    ↓
已发布 (Published) OR 发布失败 (Failed)
```

## Auto-Creation

When using the skill's auto-initialization feature, all three tables are created automatically with the correct field types and select options. No manual table creation is required.
