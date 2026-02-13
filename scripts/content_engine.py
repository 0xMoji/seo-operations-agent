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
        num_images: int = 1,
        knowledge: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate SEO-optimized content for a campaign.
        
        Args:
            campaign: Campaign settings
            platforms: Target platforms for content
            num_images: Number of images to generate
            knowledge: User-provided domain expertise (optional)
            
        Returns:
            Content dict ready for Airtable, or None on error
        """
        platforms = platforms or ["Website"]
        
        # Get available keyword
        keyword_data = self.airtable.get_available_keyword(campaign) # Assuming self.airtable is the client
        if not keyword_data:
            print("No available keywords")
            return None
        
        keyword = keyword_data["keyword"]
        existing_knowledge = keyword_data.get("knowledge", "")
        
        # Use provided knowledge or existing knowledge
        final_knowledge = knowledge or existing_knowledge
        
        # Build prompt with knowledge if available
        prompt = self._build_content_prompt(keyword, platforms, final_knowledge)
        
        try:
            content_data = self._call_openai(prompt)
            
            # Generate images for all platforms with error recovery
            images = []
            image_metadata = "[]"
            
            try:
                images_result = self.image_manager.generate_images_for_content(
                    keyword=keyword,
                    title=content_data["title"],
                    platforms=platforms,
                    num_images=num_images
                )
                
                # Convert images to format expected by Airtable
                images = [img.url for img in images_result if img.url]
                image_metadata = json.dumps([img.to_dict() for img in images_result])
                
            except Exception as img_error:
                print(f"Image generation failed: {img_error}")
                # Fallback: try to get at least one cover image from Unsplash
                try:
                    fallback_img = self.image_manager._fetch_unsplash_image(
                        keyword,
                        purpose="cover",
                        platforms=platforms
                    )
                    if fallback_img:
                        images = [fallback_img.url]
                        image_metadata = json.dumps([fallback_img.to_dict()])
                        print("✅ Fallback: Using Unsplash cover image")
                except Exception as fallback_error:
                    print(f"⚠️ Fallback also failed: {fallback_error}. Content will have no images.")
                    # Continue without images rather than failing entirely
            
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
                "images": images,
                "image_metadata": image_metadata,
                "platforms": platforms,
                "keyword": keyword,
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
    
    def _build_content_prompt(
        self, 
        keyword: str, 
        platforms: List[str],
        knowledge: Optional[str] = None
    ) -> str:
        """Build AI prompt for content generation with optional knowledge injection"""
        
        platform_instructions = {
            "Website": "完整的长文章（1500-2000字），HTML格式",
            "X (Twitter)": "280字符以内的简短版本，保留核心hashtags",
            "LinkedIn": "专业语气的中长文（500-800字）"
        }
        
        platforms_str = ", ".join([platform_instructions.get(p, p) for p in platforms])
        
        prompt = f"""
你是一位专业的 SEO 内容撰写专家。请基于以下关键词撰写一篇 SEO 优化的文章。

关键词：{keyword}
平台要求：{platforms_str}

请使用 JSON 格式返回以下内容：
{{
  "title": "吸引人的标题",
  "html_body": "HTML 格式的正文内容",
  "slug": "url-friendly-slug",
  "meta_description": "150字符以内的 SEO 描述",
  "social_snippet": "适合社交媒体分享的简短介绍",
  "keywords": ["相关", "关键词", "列表"]
}}

要求：
- 标题包含关键词，吸引点击
- 正文结构清晰，使用 <h2>, <p>, <ul> 等 HTML 标签
- 融入实用信息和具体案例
- meta_description 包含关键词和行动号召
"""
        
        # Inject user knowledge if available
        if knowledge and knowledge.strip():
            prompt += f"""

专家知识参考：
{knowledge}

请自然地融入上述专业见解和实践经验，提升内容的权威性和独特性。避免生硬堆砌，而是将这些知识点有机地整合到文章逻辑中。
"""
        
        return prompt
    
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
    
    def generate_knowledge_questions(self, keyword: str) -> List[str]:
        """
        Generate 2-3 open-ended questions to gather user knowledge.
        
        Args:
            keyword: The topic keyword
            
        Returns:
            List of questions to ask user
        """
        prompt = f"""
基于关键词 "{keyword}"，生成 3 个深入的开放式问题，用于收集领域专家的实践经验。

要求：
- 问题必须是开放式的（不是是/否问题）
- 聚焦于实践经验、独特见解或实际挑战
- 避免可以直接 Google 到答案的通用问题
- 使用中文

示例输出格式：
1. [关于实际应用场景的问题]
2. [关于独特优势或差异化的问题]
3. [关于常见障碍或挑战的问题]

只返回 3 个问题，每行一个，格式为 "1. 问题内容"
"""
        
        try:
            response = self._call_openai(prompt)
            
            # Parse questions from response
           # Extract text content
            if isinstance(response, dict) and "text" in response:
                text = response["text"]
            elif isinstance(response, str):
                text = response
            else:
                text = str(response)
            
            # Split by line and extract numbered questions
            lines = text.strip().split("\n")
            questions = []
            
            for line in lines:
                line = line.strip()
                # Match lines like "1. Question text" or "1) Question text"
                if re.match(r"^\d+[\.\)]\s+", line):
                    # Remove number prefix
                    question = re.sub(r"^\d+[\.\)]\s+", "", line)
                    questions.append(question)
            
            # Return up to 3 questions
            return questions[:3] if questions else [
                f"{keyword} 在实际项目中解决了哪些核心问题？",
                f"与传统方案相比，{keyword} 有什么独特优势？",
                f"开发者在使用 {keyword} 时通常会遇到什么挑战？"
            ]
            
        except Exception as e:
            print(f"Failed to generate questions: {e}")
            # Return fallback questions
            return [
                f"{keyword} 在实际项目中解决了哪些核心问题？",
                f"与传统方案相比，{keyword} 有什么独特优势？",
                f"开发者在使用 {keyword} 时通常会遇到什么挑战？"
            ]

