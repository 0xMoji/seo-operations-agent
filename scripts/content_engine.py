"""
Content Generation Engine

Handles AI-powered content creation using OpenClaw's configured LLM,
including article generation, SEO optimization, and multi-format output.
"""

import os
import json
from typing import Dict, Any, Optional
import requests


class ContentEngine:
    """Content generation engine using OpenAI API"""
    
    def __init__(self, airtable_client):
        self.airtable = airtable_client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        self.headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
    
    def generate(self, campaign: Dict[str, Any], channel: str = "website") -> Optional[Dict[str, Any]]:
        """
        Generate complete article with SEO metadata and social snippet
        
        Args:
            campaign: Campaign configuration
            channel: Target channel (website/twitter/linkedin)
            
        Returns:
            Article data dict or None if generation fails
        """
        # Get unused keyword
        keyword = self.airtable.get_unused_keyword()
        if not keyword:
            return None
        
        # Generate content using OpenAI
        prompt = self._build_prompt(keyword, campaign["plan_name"])
        
        try:
            content_data = self._call_openai(prompt)
            
            # Get cover image if Unsplash is configured
            cover_image = self._get_cover_image(keyword)
            
            # Mark keyword as used
            # (Would need record ID in production)
            
            return {
                "title": content_data["title"],
                "body": content_data["html_body"],
                "seo_metadata": {
                    "slug": content_data["slug"],
                    "description": content_data["meta_description"],
                    "schema_markup": self._generate_schema_markup(content_data)
                },
                "social_snippet": content_data["social_snippet"],
                "cover_image": cover_image,
                "status": "已批准" if campaign.get("auto_approve") else "待审核"
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
