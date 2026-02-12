"""
Content Generation Engine

Handles AI-powered content creation using OpenClaw's configured LLM,
including article generation, SEO optimization, and multi-format output.
"""

import os
import json
import re
from typing import Dict, Any, Optional, List
import requests


# Platform-specific character limits
PLATFORM_LIMITS = {
    "X (Twitter)": 280,
    "LinkedIn": 3000,
    "Website": None  # No limit
}


class ContentEngine:
    """Content generation engine using OpenAI API"""
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Initialize ImageManager
        from image_manager import ImageManager
        self.image_manager = ImageManager()
        
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(
        self, 
        campaign: Dict[str, Any], 
        platforms: Optional[List[str]] = None,
        num_images: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Generate complete article with SEO metadata, social snippet, and images
        
        Args:
            campaign: Campaign configuration
            platforms: Target platforms (defaults to ["Website"])
            num_images: Number of images to generate (default: 1)
            
        Returns:
            Article data dict or None if generation fails
        """
        if platforms is None:
            platforms = ["Website"]
        
        # Get unused keyword
        keyword = self.airtable.get_unused_keyword()
        if not keyword:
            return None
        
        # Generate content using OpenAI
        prompt = self._build_prompt(keyword, campaign["plan_name"])
        
        try:
            content_data = self._call_openai(prompt)
            
            # Generate images for all platforms
            images = self.image_manager.generate_images_for_content(
                keyword=keyword,
                title=content_data["title"],
                platforms=platforms,
                num_images=num_images
            )
            
            # Convert images to format expected by Airtable
            image_urls = [img.url for img in images if img.url]
            image_metadata = json.dumps([img.to_dict() for img in images])
            
            # Mark keyword as used (would need record ID in production)
            
            return {
                "title": content_data["title"],
                "body": content_data["html_body"],
                "seo_metadata": json.dumps({
                    "slug": content_data["slug"],
                    "description": content_data["meta_description"],
                    "schema_markup": self._generate_schema_markup(content_data)
                }),
                "social_snippet": content_data["social_snippet"],
                "images": image_urls,
                "image_metadata": image_metadata,
                "platforms": platforms,
                "status": "Approved" if campaign.get("auto_approve") else "Pending"
            }
        except Exception as e:
            print(f"Content generation error: {e}")
            return None
    
    def _build_prompt(self, keyword: str, topic: str) -> str:
        """Build structured prompt for content generation"""
        return f"""
你是一位专业的 SEO 内容撰写专家。请基于以下关键词撰写一篇 SEO 优化的文章。

关键词：{keyword}
主题方向：{topic}

要求：
1. 文章长度：800-1200字
2. 输出格式：HTML (使用 <article> 标签包裹)
3. 使用 H2/H3 标签构建语义化的标题层级
4. 自然融入关键词，避免过度堆砌
5. 包含实用的信息和案例

请以 JSON 格式返回以下内容：
{{
  "title": "文章标题（吸引人且包含关键词）",
  "slug": "URL友好的短链（英文，用连字符分隔）",
  "meta_description": "SEO描述（150-160字符，包含关键词）",
  "html_body": "完整的HTML文章内容",
  "social_snippet": "社交媒体摘要（<280字符，包含emoji和话题标签）"
}}

只返回 JSON，不要其他内容。
        """.strip()
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API for content generation"""
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的 SEO 内容创作专家，擅长撰写高质量、符合搜索引擎优化的文章。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.openai_url,
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        
        # Parse response
        content = response.json()["choices"][0]["message"]["content"]
        
        # Extract JSON from markdown code block if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    
    def _get_cover_image(self, keyword: str) -> Optional[str]:
        """Get cover image from Unsplash or return None"""
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        if not unsplash_key:
            return None
        
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": keyword,
                "per_page": 1,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {unsplash_key}"
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if results:
                # Return regular size URL (Airtable will download and cache)
                return results[0]["urls"]["regular"]
            
        except Exception as e:
            print(f"Unsplash fetch error: {e}")
        
        return None
    
    def _generate_schema_markup(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON-LD schema markup for SEO"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": content_data["title"],
            "description": content_data["meta_description"],
            "author": {
                "@type": "Organization",
                "name": "Your Organization"  # Should be configurable
            },
            "datePublished": "",  # Will be filled at publish time
            "keywords": content_data.get("meta_keywords", "")
        }
    
    def generate_for_platforms(
        self, 
        campaign: Dict[str, Any], 
        platforms: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate platform-specific content for multiple channels.
        
        Args:
            campaign: Campaign configuration
            platforms: List of platforms (e.g., ["X (Twitter)", "LinkedIn", "Website"])
            
        Returns:
            Dict mapping platform to content data
        """
        # Get unused keyword
        keyword = self.airtable.get_unused_keyword()
        if not keyword:
            return {}
        
        results = {}
        
        for platform in platforms:
            try:
                if platform == "X (Twitter)":
                    content = self._generate_twitter_content(keyword, campaign)
                elif platform == "LinkedIn":
                    content = self._generate_linkedin_content(keyword, campaign)
                elif platform == "Website":
                    content = self.generate(campaign, "website")
                else:
                    continue
                
                if content:
                    results[platform] = content
                    
            except Exception as e:
                print(f"Failed to generate content for {platform}: {e}")
        
        return results
    
    def _generate_twitter_content(
        self, 
        keyword: str, 
        campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Twitter-optimized content (max 280 chars)"""
        prompt = f"""
Create a Twitter post about: {keyword}
Topic context: {campaign['plan_name']}

Requirements:
- Maximum 280 characters (strict limit)
- Engaging and conversational tone
- Include 1-2 relevant emojis
- Add 2-3 hashtags at the end
- Call-to-action or thought-provoking question

Return JSON:
{{
  "text": "Tweet content",
  "title": "Short title for tracking"
}}
"""
        
        content_data = self._call_openai(prompt)
        
        # Enforce 280 character limit
        text = self._enforce_platform_limit(content_data["text"], "X (Twitter)")
        
        return {
            "title": content_data.get("title", f"Twitter: {keyword}"),
            "body": text,
            "platform": "X (Twitter)",
            "status": "Approved" if campaign.get("auto_approve") else "Pending"
        }
    
    def _generate_linkedin_content(
        self, 
        keyword: str, 
        campaign: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate LinkedIn-optimized content (max 3000 chars)"""
        prompt = f"""
Create a LinkedIn post about: {keyword}
Topic context: {campaign['plan_name']}

Requirements:
- Maximum 3000 characters
- Professional yet engaging tone
- Include industry insights or data
- Use line breaks for readability
- End with a thoughtful question
- 3-5 relevant hashtags

Return JSON:
{{
  "text": "LinkedIn post content",
  "title": "Headline for tracking"
}}
"""
        
        content_data = self._call_openai(prompt)
        
        # Enforce 3000 character limit
        text = self._enforce_platform_limit(content_data["text"], "LinkedIn")
        
        return {
            "title": content_data.get("title", f"LinkedIn: {keyword}"),
            "body": text,
            "platform": "LinkedIn",
            "status": "Approved" if campaign.get("auto_approve") else "Pending"
        }
    
    def _enforce_platform_limit(self, content: str, platform: str) -> str:
        """
        Ensure content fits within platform character limits.
        
        Args:
            content: Original content text
            platform: Target platform name
            
        Returns:
            Truncated content if necessary
        """
        limit = PLATFORM_LIMITS.get(platform)
        
        if limit is None or len(content) <= limit:
            return content
        
        # Smart truncation: preserve hashtags and emojis when possible
        return self._truncate_smartly(content, limit)
    
    def _truncate_smartly(self, text: str, limit: int) -> str:
        """
        Intelligently truncate text while preserving hashtags.
        
        Strategy:
        1. Extract hashtags from end
        2. Truncate main content
        3. Re-append hashtags if space allows
        4. Add ellipsis
        """
        # Extract hashtags (assuming they're at the end)
        hashtag_pattern = r'((?:#\w+\s*)+)$'
        hashtag_match = re.search(hashtag_pattern, text)
        
        if hashtag_match:
            hashtags = hashtag_match.group(1).strip()
            main_text = text[:hashtag_match.start()].strip()
        else:
            hashtags = ""
            main_text = text
        
        # Calculate available space
        hashtag_space = len(hashtags) + 1 if hashtags else 0  # +1 for space
        ellipsis = "..."
        available = limit - hashtag_space - len(ellipsis)
        
        if available <= 0:
            # Can't fit hashtags, just truncate all
            return text[:limit-len(ellipsis)] + ellipsis
        
        # Truncate at word boundary
        truncated = main_text[:available].rsplit(' ', 1)[0]
        
        # Reassemble
        result = truncated + ellipsis
        if hashtags and (len(result) + hashtag_space) <= limit:
            result += " " + hashtags
        
        return result
