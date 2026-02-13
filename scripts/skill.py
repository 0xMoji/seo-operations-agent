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
        Process user message with priority state detection.
        
        Priority 1: Check if awaiting answers for knowledge collection
        Priority 2: Normal intent parsing
        """
        
        # Priority 1: Check for keyword awaiting answers
        awaiting_kw = self.airtable.get_keyword_awaiting_answers()
        
        if awaiting_kw:
            # Check if user wants to skip
            if any(skip_word in message.lower() for skip_word in ["跳过", "直接生成", "skip"]):
                return self._skip_knowledge_collection(awaiting_kw)
            
            # Otherwise, treat message as answers
            return self._process_knowledge_answers(awaiting_kw, message)
        
        # Priority 2: Normal intent parsing
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
        """
        Manually generate content with knowledge collection support.
        
        Checks Collection Status and triggers knowledge collection if needed.
        """
        # Get active campaign
        campaigns = self.airtable.get_active_campaigns()
        if not campaigns:
            return "⚠️ 请先创建运营计划。"
        
        campaign = campaigns[0]
        
        # Get next available keyword with collection status
        keyword_data = self.airtable.get_available_keyword(campaign)
        
        if not keyword_data:
            return "⚠️ 关键词库为空，请先添加关键词"
        
        keyword = keyword_data["keyword"]
        record_id = keyword_data["record_id"]
        collection_status = keyword_data.get("collection_status", "Needs Knowledge")
        
        # Check collection status and route accordingly
        if collection_status == "Needs Knowledge":
            # Start knowledge collection
            return self._start_knowledge_collection(keyword, record_id)
        
        elif collection_status == "Awaiting Answers":
            # Already asked, waiting for user
            return f"""
💬 我正在等待您回答关于 "{keyword}" 的问题

请回答之前的问题，或说"跳过"直接生成内容。
"""
        
        # Collection status is "Ready" or "Skipped" - proceed with generation
        knowledge = keyword_data.get("knowledge", "")
        
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
    
    def _start_knowledge_collection(self, keyword: str, record_id: str) -> str:
        """Generate questions and wait for user answers"""
        
        # Generate questions using content engine
        questions = self.content_engine.generate_knowledge_questions(keyword)
        
        # Save questions to Airtable
        import json
        questions_json = json.dumps(questions, ensure_ascii=False)
        self.airtable.update_keyword_collection_status(
            record_id,
            status="Awaiting Answers",
            pending_questions=questions_json
        )
        
        # Format message for user
        questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
        
        return f"""
📝 关键词: "{keyword}"

为了让内容更专业，请分享您对这个主题的见解：

{questions_text}

💬 请回答上述问题（可以简短回答，或说"跳过"直接生成）
"""
    
    def _process_knowledge_answers(
        self, 
        keyword_data: Dict[str, Any],
        user_message: str
    ) -> str:
        """Parse user answers and save knowledge"""
        
        import json
        
        keyword = keyword_data["keyword"]
        record_id = keyword_data["record_id"]
        questions = json.loads(keyword_data["pending_questions"])
        
        # Use AI to structure the answers
        parse_prompt = f"""
用户回答了以下关于 "{keyword}" 的问题：

问题列表：
{chr(10).join(f'{i+1}. {q}' for i, q in enumerate(questions))}

用户的回答：
{user_message}

请将回答结构化整理，格式如下：

Q1: [第一个问题]
A1: [用户的答案]

Q2: [第二个问题]
A2: [用户的答案]

Q3: [第三个问题]
A3: [用户的答案]

如果用户没有明确回答某个问题，A 部分写"未提及"。
只返回结构化的 Q&A，不要其他内容。
"""
        
        try:
            # Parse answers using OpenAI
            response = self.content_engine._call_openai(parse_prompt)
            
            # Extract text
            if isinstance(response, dict):
                structured_knowledge = response.get("text", str(response))
            else:
                structured_knowledge = str(response)
            
            # Save knowledge and mark as ready
            self.airtable.update_keyword_collection_status(
                record_id,
                status="Ready",
                knowledge=structured_knowledge,
                pending_questions=""
            )
            
            # Auto-generate content after collecting knowledge
            return self._auto_generate_after_knowledge(keyword, record_id, structured_knowledge)
            
        except Exception as e:
            print(f"Error processing answers: {e}")
            return f"⚠️ 处理回答时出错，请重新回答或说"跳过""
    
    def _skip_knowledge_collection(self, keyword_data: Dict[str, Any]) -> str:
        """Skip knowledge collection and generate directly"""
        
        keyword = keyword_data["keyword"]
        record_id = keyword_data["record_id"]
        
        # Mark as skipped
        self.airtable.update_keyword_collection_status(
            record_id,
            status="Skipped",
            pending_questions=""
        )
        
        # Generate without knowledge
        return f"⏭️ 已跳过知识收集，正在生成关于 \"{keyword}\" 的文章..."
    
    def _auto_generate_after_knowledge(
        self,
        keyword: str,
        record_id: str,
        knowledge: str
    ) -> str:
        """Automatically generate content after knowledge is collected"""
        
        # Get active campaign
        campaigns = self.airtable.get_active_campaigns()
        if not campaigns:
            return "⚠️ 请先创建运营计划"
        
        campaign = campaigns[0]
        
        # Determine platforms
        platforms = []
        if campaign.get("website_webhook_url"):
            platforms.append("Website")
        
        buffer_channels = campaign.get("buffer_channels", [])
        if "twitter" in buffer_channels:
            platforms.append("X (Twitter)")
        if "linkedin" in buffer_channels:
            platforms.append("LinkedIn")
        
        if not platforms:
            platforms = ["Website"]
        
        # Generate article with knowledge
        article = self.content_engine.generate(
            campaign,
            platforms=platforms,
            num_images=2 if "Website" in platforms else 1,
            knowledge=knowledge
        )
        
        if not article:
            return "⚠️ 内容生成失败"
        
        # Save to Airtable
        content_id = self.airtable.create_content(article)
        
        # Build review link
        airtable_link = self.scheduler.generate_airtable_link()
        
        return f"""
✅ 已生成融合您专业见解的文章！

📄 标题: "{article['title']}"

💡 文章已自然融入您提到的专业知识点

👉 请前往 Airtable 审核：
{airtable_link}

审核后将状态改为 "Approved" 即可发布。
"""

