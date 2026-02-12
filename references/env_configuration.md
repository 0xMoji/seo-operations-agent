# Environment Configuration Reference

Complete guide for all environment variables used by the SEO Operations Agent skill.

## Required Configuration

### Core API Keys

```bash
# OpenAI API (Required for content generation)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxx

# Airtable API (Required for content hub)
AIRTABLE_API_KEY=patxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX  # Created automatically if not provided
```

## Optional Configuration

### Image Generation

```bash
# Choose default image generation method
IMAGE_GENERATION_MODEL=dall-e-3  # Options: dall-e-3, dall-e-2, stable-diffusion, unsplash-only

# For DALL-E (uses OPENAI_API_KEY above, no extra config needed)

# For Stable Diffusion API (if using custom provider)
STABILITY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# For stock photos (fallback or primary source)
UNSPLASH_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Website Direct Publishing

```bash
# Website API endpoint
WEBSITE_API_ENDPOINT=https://yoursite.com/api/posts

# Authentication method
WEBSITE_AUTH_METHOD=api_key  # Options: api_key, bearer, basic, oauth, none

# Credentials (based on auth method)
WEBSITE_API_KEY=your_api_key_here             # For api_key method
WEBSITE_OAUTH_TOKEN=your_oauth_token           # For bearer method
WEBSITE_USERNAME=your_username                 # For basic method
WEBSITE_PASSWORD=your_password                 # For basic method

# Optional custom headers (JSON format)
WEBSITE_CUSTOM_HEADERS={"X-Custom-Header": "value"}
```

### Make.com Integration

```bash
# Webhook URL from Make.com scenario
MAKECOM_WEBHOOK_URL=https://hook.us2.make.com/xxxxxxxxxxxxxxx
```

## Platform-Specific Examples

### WordPress

```bash
WEBSITE_API_ENDPOINT=https://yoursite.com/wp-json/wp/v2/posts
WEBSITE_AUTH_METHOD=basic
WEBSITE_USERNAME=your_wp_username
WEBSITE_PASSWORD=your_application_password  # Generate in WP Admin → Users → Application Passwords
```

### Strapi CMS

```bash
WEBSITE_API_ENDPOINT=https://yoursite.com/api/articles
WEBSITE_AUTH_METHOD=bearer
WEBSITE_OAUTH_TOKEN=your_strapi_api_token  # From Strapi Settings → API Tokens
```

### Ghost CMS

```bash
WEBSITE_API_ENDPOINT=https://yoursite.com/ghost/api/admin/posts
WEBSITE_AUTH_METHOD=bearer
WEBSITE_OAUTH_TOKEN=your_admin_api_key
WEBSITE_CUSTOM_HEADERS={"Accept-Version": "v5.0"}
```

### Custom REST API

```bash
WEBSITE_API_ENDPOINT=https://api.yoursite.com/v1/blog/posts
WEBSITE_AUTH_METHOD=api_key
WEBSITE_API_KEY=your_secret_key
```

## Image Source Priority

The skill uses this priority order for images:

1. **AI Generation** (if `IMAGE_GENERATION_MODEL` is set to DALL-E or Stable Diffusion)
   - Best for: Custom branded images, social media graphics
   - Cost: ~$0.040 per image (DALL-E 3 standard quality)

2. **Unsplash** (if `UNSPLASH_ACCESS_KEY` is set)
   - Best for: Professional stock photos, blog covers
   - Cost: Free (with attribution)

3. **Manual Upload** (always available)
   - User provides images via chat or Airtable
   - Cost: Free

**Example configurations**:

```bash
# AI-first approach (for branded content)
IMAGE_GENERATION_MODEL=dall-e-3
OPENAI_API_KEY=sk-xxxxx
UNSPLASH_ACCESS_KEY=xxxxx  # Fallback

# Stock photos only (cost-effective)
IMAGE_GENERATION_MODEL=unsplash-only
UNSPLASH_ACCESS_KEY=xxxxx

# Hybrid (AI for social, stock for website)
IMAGE_GENERATION_MODEL=dall-e-3
OPENAI_API_KEY=sk-xxxxx
UNSPLASH_ACCESS_KEY=xxxxx
```

## Validation

Test your configuration with:

```python
# Check Airtable connection
from airtable_client import AirtableClient
client = AirtableClient()
print(client.is_configured())

# Check image generation
from image_manager import ImageManager
img_mgr = ImageManager()
test_img = img_mgr.generate_cover_image("test keyword", "Test Title", ["Website"])

# Check website publishing
from website_publisher import WebsitePublisher
publisher = WebsitePublisher()
result = publisher.test_connection()
print(result)
```

## Security Best Practices

1. **Never commit `.env` to Git**
   - Already in `.gitignore` by default

2. **Use environment-specific files**
   - `.env.development` for testing
   - `.env.production` for live campaigns

3. **Rotate API keys regularly**
   - Especially for high-value production systems

4. **Principle of least privilege**
   - Grant minimum required permissions:
     - Airtable: `data.records:read`, `data.records:write`, `schema.bases:write`
     - Website API: Create posts only (not delete/modify)

## Troubleshooting

### "OPENAI_API_KEY not set"

- Verify `.env` file exists in skill root directory
- Check no typos in variable name
- Restart OpenClaw after adding variables

### "Airtable base_id required"

- On first run, skill will auto-create base and output the ID
- Copy ID to `.env` as `AIRTABLE_BASE_ID`
- Or let it auto-create every time (less efficient)

### Images not generating

1. Check `IMAGE_GENERATION_MODEL` value
2. Verify corresponding API key is set (OPENAI_API_KEY or STABILITY_API_KEY)
3. Check API quota/billing
4. Fallback to Unsplash if available

### Website publishing fails

1. Test endpoint with `curl`:
   ```bash
   curl -X POST https://yoursite.com/api/posts \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Test"}'
   ```
2. Check auth method matches your API's requirements
3. Review website API logs for error details
