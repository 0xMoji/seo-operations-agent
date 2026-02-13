---
name: seo-operations-agent
description: Automated SEO content generation, scheduling, and multi-platform distribution with Airtable integration. Use when the user needs to (1) Create an automated SEO content pipeline, (2) Generate SEO-optimized articles from keywords, (3) Set up scheduled content publishing, (4) Manage content campaigns with Airtable, (5) Distribute content to multiple platforms (website/social media), (6) Automate content inventory monitoring, or (7) mentions running SEO campaigns, content automation, or SEO operations.
---

# AI SEO Operations Agent

A fully automated, private SEO content generation and distribution system built for OpenClaw. This skill enables zero-cost, zero-server SEO operations with complete data privacy.

## Features

- 🧠 **Smart Content Generation**: AI-powered article creation with SEO optimization
- 💡 **Knowledge Injection** (v2.1): Automatically collects your domain expertise before generating content
- 🎨 **Flexible Image Generation** (v2.2): Support for 8+ AI image providers (OpenAI, Google, Stability AI, etc.)
- 📅 **Automated Scheduling**: Set-and-forget content calendar management
- 🔔 **Intelligent Reminders**: Pre-publish notifications and content inventory monitoring
- 🌐 **Multi-Platform Distribution**: Website + X (Twitter) + LinkedIn with platform-specific content
- 🔒 **Full Privacy**: All data stays in your Airtable, zero third-party storage
- 💰 **BYOK Model**: You control all API costs (OpenAI, Airtable, Unsplash/DALL-E)

## Quick Start

### 1. Initial Setup

First time using the skill? Just say:

```
我想启动 SEO 自动化
```

The agent will guide you through:
- Connecting your Airtable account (just need API token)
- **Auto-creating Airtable base and tables** (no manual setup needed!)
- Configuring Make.com webhook
- (Optional) Setting up Unsplash for images

**What gets created automatically**:
- ✅ New Airtable base: "SEO Content Hub"
- ✅ Campaign_Settings table (9 fields)
- ✅ Keyword_Pool table (3 fields)
- ✅ Content_Hub table (9 fields)

You'll get a direct link to your new base!

### 2. Create a Campaign

```
启动一个为期 30 天的计划，主题是 Web3 隐私技术，每天 1 篇
```

You'll be prompted for:
- **Website webhook URL** (optional): For custom site publishing
- **Social media channels**: twitter, linkedin, bluesky
- **Publish time**: e.g., "10:00"

### 3. Add Keywords

```
把这些关键词加到词库里：zkProof, 零知识证明, Web3 身份
```

The agent will:
- Add keywords to your pool
- Auto-check content inventory
- Generate articles if any channel has < 10 pieces

### 4. Knowledge Collection (v2.1 - Automated)

When generating content, the agent will **automatically** ask you 3 questions about the keyword:

```
Agent: 📝 关键词: "零知识证明"
       
       为了让内容更专业，请分享您对这个主题的见解：
       
       1. 零知识证明在实际项目中解决了哪些核心问题？
       2. 与传统方案相比，有什么独特优势？
       3. 开发者在使用时通常会遇到什么挑战？
       
       💬 请回答（或说"跳过"直接生成）

You: 1. 跨链身份验证和隐私交易
     2. 不解密也能计算
     3. 性能开销大
```

The agent will:
- Parse your answers using AI
- Naturally integrate your expertise into the article
- Save knowledge for future reference

**Skip option**: Say "跳过" to generate without knowledge collection.

### 5. Manual Content Generation

```
现在生成内容
```

或

```
生成 5 篇文章
```

### 6. Review Content

After generation, you'll receive an Airtable link:

```
✅ 已生成 5 篇文章，已保存到 Airtable

👉 请前往 Airtable 审核内容：
https://airtable.com/appXXXXXX/tblYYYYYY/viwZZZZZZ
```

Change status from **"Pending"** to **"Approved"** when ready to publish.

### 6. Automated Publishing

The agent will:
- **3 hours before publish time**: Send reminder with content summary
- **At publish time**: Trigger Make.com to distribute approved content

## Advanced Commands

### Campaign Management

```bash
# Stop current campaign
停止当前的 SEO 计划

# Check progress
汇报一下当前的运营进度

# Manual publish trigger
trigger_publish
```

### Content Operations

```bash
# Postpone article
把刚才那篇文章的发布推迟
```

### Image Management (v2.2 - Flexible Configuration)

The skill **auto-detects** configured image providers and asks for confirmation:

```bash
# Option 1: OpenAI DALL-E
OPENAI_API_KEY=sk-...

# Option 2: Google Imagen
GOOGLE_API_KEY=your-key

# Option 3: Stability AI
STABILITY_API_KEY=sk-...

# Option 4: Replicate
REPLICATE_API_TOKEN=r8_...

# Option 5: Custom API (any provider)
IMAGE_API_KEY=your-key
IMAGE_API_ENDPOINT=https://api.xxx.com/generate
IMAGE_MODEL=flux-schnell
IMAGE_PROVIDER=MyProvider

# Stock photography fallback
UNSPLASH_ACCESS_KEY=xxx
```

**Supported providers**: OpenAI, Google Imagen, Stability AI, Replicate, RunPod, Together AI, Hugging Face, Custom

The skill automatically:
- Detects configured providers from env vars
- Asks which one to use if multiple found
- Generates cover images for all platforms
- Adds inline images for website articles
- Creates social media thumbnails for Twitter/LinkedIn
- Tracks image positions in Airtable metadata

## Architecture

```
OpenClaw (Scheduler)
    ↓
Airtable (Content Hub)
    ↓
Make.com (Automation)
    ↓
├─→ Custom Website (Webhook)
└─→ Buffer → Social Media
```

## Data Schema

The skill uses three Airtable tables: Campaign_Settings, Keyword_Pool, and Content_Hub.

For complete field definitions and schema details, see [references/airtable_schema.md](references/airtable_schema.md).

## Configuration

The skill requires minimal configuration - just an Airtable API token to get started. The base and tables are created automatically.

For environment variables, service tier requirements, and detailed setup instructions, see [references/configuration.md](references/configuration.md).

## Content Format

The skill generates dual-format content:

1. **HTML Article** (for websites): Full semantic HTML with SEO metadata
2. **Social Snippet** (for Buffer): Concise post with emojis and hashtags

## Make.com Integration

The skill works with Make.com to handle multi-platform distribution. See [references/makecom_setup.md](references/makecom_setup.md) for scenario template and configuration.

## Privacy & Security

- ✅ **No centralized server**: All processing happens in OpenClaw
- ✅ **Data isolation**: Content only exists in your Airtable
- ✅ **API key ownership**: You control all service credentials
- ✅ **Audit trail**: Full visibility in Airtable records

## Cost Estimate

Based on 30 articles/month:

- **OpenAI** (GPT-4): ~$3-5/month
- **Unsplash**: Free (50 requests/hour limit)
- **Airtable**: Free tier sufficient
- **Make.com**: Free tier sufficient
- **Total**: ~$3-5/month

## Additional Resources

- [Setup Guide](references/setup_guide.md) - Complete installation instructions
- [Make.com Setup](references/makecom_setup.md) - Distribution automation
- [Auto-Initialization](references/auto_init_example.md) - How automatic base creation works
- [Airtable Schema](references/airtable_schema.md) - Database structure reference
- [Configuration](references/configuration.md) - Environment variables and settings

## License

MIT License - Use freely in your projects.
