"""
AI SEO Operations Agent - Core Skill Module

This module provides the main entry point for the OpenClaw skill,
handling conversational intent parsing and orchestrating the full
SEO content automation workflow.
"""

import os
import re
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

from .airtable_client import AirtableClient
from .content_engine import ContentEngine
from .scheduler import CampaignScheduler
from .intent_parser import IntentParser


class SEOAgent:
    """Main skill class for SEO operations automation"""
    
    def __init__(self):
        self.airtable = AirtableClient()
        self.content_engine = ContentEngine(self.airtable)
        self.scheduler = CampaignScheduler(self.airtable, self.content_engine)
        self.parser = IntentParser()
        
        # Start background scheduler
        self.scheduler.start()
    
    def process_message(self, message: str) -> str:
        """
        Process user message and execute corresponding action
        
        Args:
            message: User's natural language input
            
        Returns:
            Agent's response message
        """
        intent = self.parser.parse(message)
        
        if intent.type == "setup":
            return self._handle_setup()
        elif intent.type == "create_campaign":
            return self._handle_create_campaign(intent.params)
        elif intent.type == "add_keywords":
            return self._handle_add_keywords(intent.params)
        elif intent.type == "generate_content":
            return self._handle_generate_content(intent.params)
        elif intent.type == "status_query":
            return self._handle_status_query()
        elif intent.type == "stop_campaign":
            return self._handle_stop_campaign()
        elif intent.type == "manual_trigger":
            return self._handle_manual_trigger()
        else:
            return "抱歉，我不理解这个指令。请尝试：'启动 SEO 计划'、'添加关键词'或'生成内容'。"
    
    def _handle_setup(self) -> str:
        """Guide user through initial configuration"""
        # Check if Airtable API key is configured
        if not os.getenv("AIRTABLE_API_KEY"):
            return """
检测到首次使用，需要配置 Airtable API Token：

1. 访问 https://airtable.com/create/tokens
2. 创建新 Token，名称：SEO Agent
3. 添加以下权限：
   - data.records:read
   - data.records:write
   - schema.bases:read
   - schema.bases:write
4. 将 Token 添加到 .env 文件：
   AIRTABLE_API_KEY=your_token_here

配置完成后，重新运行 skill 或输入"初始化系统"。
            """
        
        # API key exists, check/create base
        result = self.airtable.check_and_initialize_base()
        
        if result["status"] == "error":
            return f"❌ 配置错误：{result['message']}"
        
        elif result["status"] == "exists":
            return f"""
✅ Airtable 已配置完成！

Base ID: {result['base_id']}
所有表结构已就绪。

🎯 下一步：创建你的第一个运营计划
示例：启动一个为期 30 天的计划，主题是 Web3 隐私技术，每天 1 篇
            """
        
        elif result["status"] == "created":
            # Save base_id to .env
            self._update_env_file("AIRTABLE_BASE_ID", result["base_id"])
            
            return f"""
✅ Airtable Base Auto-Created Successfully!

📊 Base: SEO Content Hub  
🔗 Access: {result['base_url']}

📋 Tables Created:
• Campaign_Settings - Your SEO campaigns
• Keyword_Pool - Content keywords  
• Content_Hub - Generated articles

⚙️ Configuration:
Base ID has been saved to .env file.
Please restart the skill to apply changes.

🎯 Next Steps:
1. Restart this skill
2. Create your first campaign
   Example: "启动一个为期 30 天的计划，主题是 Web3 隐私技术，每天 1 篇"
            """.strip()
        
        elif result["status"] == "updated":
            return f"""
✅ 已补充缺失的表结构

{result['message']}

系统已就绪，可以开始创建运营计划。
            """
    
    def _update_env_file(self, key: str, value: str):
        """Update or add key to .env file"""
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        
        # Read existing content
        lines = []
        key_exists = False
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # Update or append
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                key_exists = True
            else:
                new_lines.append(line)
        
        if not key_exists:
            new_lines.append(f"{key}={value}\n")
        
        # Write back
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    
    def _handle_create_campaign(self, params: Dict[str, Any]) -> str:
        """Create new SEO campaign with user interaction"""
        duration = params.get("duration", 30)
        topic = params.get("topic", "")
        frequency = params.get("frequency", 1)
        
        # Input validation
        if duration <= 0 or duration > 365:
            return "❌ Campaign duration must be between 1-365 days."
        
        if frequency <= 0 or frequency > 10:
            return "❌ Frequency must be between 1-10 articles per day."
        
        if not topic or len(topic.strip()) == 0:
            return "❌ Please provide a valid campaign topic."
        
        start_date = date.today()
        end_date = start_date + timedelta(days=duration)
        
        # Validate date range
        if end_date <= start_date:
            return "❌ End date must be after start date."
        
        # Interactive prompts for additional config
        # (In real implementation, this would be multi-turn conversation)
        
        campaign_id = self.airtable.create_campaign({
            "plan_name": f"{topic} SEO Campaign",
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "publish_time": "10:00",  # Default, should prompt user
            "auto_approve": False,
            "is_active": True,
            "website_webhook_url": None,
            "buffer_channels": ["twitter"]
        })
        
        return f"""
✅ 运营计划已创建！

📋 计划概况：
- 主题：{topic}
- 周期：{duration} 天
- 频率：每天 {frequency} 篇
- 发布时间：10:00 (可修改)

🎯 下一步：添加关键词
示例：把这些关键词加到词库里：关键词1, 关键词2, 关键词3
        """
    
    def _handle_add_keywords(self, params: Dict[str, Any]) -> str:
        """Add keywords to pool and check content inventory"""
        keywords = params.get("keywords", [])
        
        # Input validation
        if not keywords or len(keywords) == 0:
            return "❌ Please provide at least one keyword."
        
        # Filter out empty strings
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        
        if not keywords:
            return "❌ No valid keywords provided."
        
        # Add to Airtable
        added_count = self.airtable.add_keywords(keywords)
        
        # Auto-check and generate if needed
        generated_summary = self.scheduler.auto_generate_if_needed()
        
        response = f"✅ 已添加 {added_count} 个关键词。"
        
        if generated_summary:
            response += f"\n\n{generated_summary}"
        
        return response
    
    def _handle_generate_content(self, params: Dict[str, Any]) -> str:
        """Manually generate content immediately"""
        count = params.get("count", 5)
        
        # Get active campaign
        campaigns = self.airtable.get_active_campaigns()
        if not campaigns:
            return "⚠️ 请先创建运营计划。"
        
        campaign = campaigns[0]
        
        # Determine platforms from campaign
        platforms = []
        if campaign.get("website_webhook_url"):
            platforms.append("Website")
        
        buffer_channels = campaign.get("buffer_channels", [])
        if "twitter" in buffer_channels:
            platforms.append("X (Twitter)")
        if "linkedin" in buffer_channels:
            platforms.append("LinkedIn")
        
        # Default to Website if no platforms configured
        if not platforms:
            platforms = ["Website"]
        
        # Generate articles with proper parameters
        generated = []
        for i in range(count):
            article = self.content_engine.generate(
                campaign,
                platforms=platforms,
                num_images=2 if "Website" in platforms else 1  # More images for website
            )
            if article:
                record_id = self.airtable.create_content(article)
                generated.append(article["title"])
        
        # Build review link
        airtable_link = self.scheduler.generate_airtable_link()
        
        return f"""
✅ 已生成 {len(generated)} 篇文章，已保存到 Airtable

📋 内容概览：
{chr(10).join(f'{i+1}. "{title}"' for i, title in enumerate(generated))}

👉 请前往 Airtable 审核内容：
{airtable_link}

After review, change the status to \"Approved\" to proceed.
        """
    
    def _handle_status_query(self) -> str:
        """Report current campaign progress"""
        campaigns = self.airtable.get_active_campaigns()
        
        if not campaigns:
            return "当前没有活跃的运营计划。"
        
        campaign = campaigns[0]
        
        # Get statistics
        stats = self.airtable.get_campaign_stats(campaign["id"])
        
        days_elapsed = (date.today() - campaign["start_date"]).days
        days_total = (campaign["end_date"] - campaign["start_date"]).days
        progress = int((days_elapsed / days_total) * 100)
        
        return f"""
📊 运营进度汇报

📅 计划：{campaign["plan_name"]}
⏱️ 进度：{days_elapsed}/{days_total} 天 ({progress}%)

📝 内容统计：
- 总关键词：{stats['total_keywords']} 个
- 已使用：{stats['used_keywords']} 个
- Pending: {stats['pending_articles']} articles
- Approved: {stats['approved_articles']} articles
- Published: {stats['published_articles']} articles

🎯 Today's Progress: {stats['today_published']}/{campaign['frequency']} published
        """
    
    def _handle_stop_campaign(self) -> str:
        """Deactivate all campaigns"""
        count = self.airtable.deactivate_all_campaigns()
        return f"✅ 已停止 {count} 个活跃计划。"
    
    def _handle_manual_trigger(self) -> str:
        """Manually trigger Make.com publication"""
        self.scheduler.trigger_makecom()
        return "✅ 已触发 Make.com 发布流程。请稍等 1-2 分钟查看结果。"


# Skill entry point for OpenClaw
def main():
    """Initialize and run the SEO agent"""
    agent = SEOAgent()
    
    # In real OpenClaw integration, this would connect to conversation loop
    print("SEO Operations Agent initialized and running...")
    
    # Keep scheduler running
    import time
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
