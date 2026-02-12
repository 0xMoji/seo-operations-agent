"""
Campaign Scheduler

Background daemon for automated content generation, pre-publish reminders,
and scheduled publishing triggers.
"""

import os
import time
import threading
import requests
from datetime import datetime, date, timedelta
from typing import Optional


class CampaignScheduler:
    """Automated scheduler for SEO campaigns"""
    
    def __init__(self, airtable_client, content_engine):
        self.client = airtable_client
        self.engine = content_engine
        self.running = False
        self._last_reminder_check = None
        self._last_publish_check = None
    
    def start(self):
        """Launch background scheduler thread"""
        if self.running:
            return
        
        self.running = True
        thread = threading.Thread(target=self._poll_loop, daemon=True)
        thread.start()
        print("✅ Campaign scheduler started")
    
    def stop(self):
        """Stop scheduler gracefully"""
        self.running = False
    
    def _poll_loop(self):
        """Main polling loop - checks every minute"""
        while self.running:
            try:
                now = datetime.now()
                
                # Hourly: Check content inventory and auto-generate
                if now.minute == 0:
                    self.auto_generate_if_needed()
                
                # Every 5 minutes: Check for pre-publish reminders
                if now.minute % 5 == 0:
                    self._check_pre_publish_reminders()
                
                # Every minute: Check for publish time triggers
                self._check_publish_time()
                
            except Exception as e:
                print(f"Scheduler error: {e}")
            
            time.sleep(60)  # Wait 1 minute
    
    def auto_generate_if_needed(self) -> Optional[str]:
        """
        Auto-generate content if inventory falls below threshold
        
        Returns:
            Summary message or None
        """
        campaigns = self.client.get_active_campaigns()
        if not campaigns:
            return None
        
        generated_summary = []
        
        for campaign in campaigns:
            for channel in campaign.get("buffer_channels", []):
                count = self.client.count_pending_content(channel)
                
                if count < 10:
                    keywords_needed = 10 - count
                    
                    # Generate articles
                    for _ in range(keywords_needed):
                        article = self.engine.generate(campaign, channel)
                        if article:
                            self.client.create_content(article)
                    
                    generated_summary.append(
                        f"检测到 {channel} 渠道剩余内容不足，已自动生成 {keywords_needed} 篇文章"
                    )
        
        if generated_summary:
            message = "\n".join(generated_summary)
            self._notify_user(message)
            return message
        
        return None
    
    def _check_pre_publish_reminders(self):
        """Send reminder 3 hours before publish time"""
        now = datetime.now()
        
        # Prevent duplicate reminders in the same 5-minute window
        current_window = (now.hour, now.minute // 5)
        if self._last_reminder_check == current_window:
            return
        self._last_reminder_check = current_window
        
        campaigns = self.client.get_active_campaigns()
        
        for campaign in campaigns:
            publish_time_str = campaign.get("publish_time", "10:00")
            
            try:
                publish_time = datetime.strptime(publish_time_str, "%H:%M").time()
                reminder_time = (
                    datetime.combine(date.today(), publish_time) - timedelta(hours=3)
                ).time()
                
                # Check if we're within 5 minutes of reminder time
                if (now.hour == reminder_time.hour and 
                    abs(now.minute - reminder_time.minute) < 5):
                    
                    pending = self.client.count_records("待审核")
                    approved = self.client.count_records("已批准")
                    
                    if pending > 0:
                        airtable_link = self.generate_airtable_link(filter="待审核")
                        
                        message = f"""
⏰ 今日发布提醒 (3 小时后发布)

📅 发布计划：
- 时间：{publish_time_str}
- 待审核文章：{pending} 篇
- 已批准文章：{approved} 篇

⚠️ 请尽快前往 Airtable 审核：
{airtable_link}
                        """.strip()
                        
                        self._notify_user(message)
            
            except Exception as e:
                print(f"Reminder check error: {e}")
    
    def _check_publish_time(self):
        """Trigger Make.com at scheduled publish time"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Prevent duplicate triggers in the same minute
        if self._last_publish_check == current_time:
            return
        self._last_publish_check = current_time
        
        campaigns = self.client.get_active_campaigns()
        
        for campaign in campaigns:
            if campaign.get("publish_time") == current_time:
                approved_count = self.client.count_records("已批准")
                
                if approved_count > 0:
                    self.trigger_makecom()
                    print(f"✅ Triggered Make.com for {approved_count} approved articles")
    
    def trigger_makecom(self):
        """Send webhook to Make.com to initiate distribution"""
        webhook_url = os.getenv("MAKECOM_WEBHOOK_URL")
        
        if not webhook_url:
            print("⚠️ MAKECOM_WEBHOOK_URL not configured")
            return
        
        try:
            payload = {
                "action": "publish",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            print(f"✅ Make.com webhook triggered: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Make.com trigger failed: {e}")
    
    def generate_airtable_link(self, filter: Optional[str] = None) -> str:
        """
        Generate deep link to Airtable view
        
        Args:
            filter: Optional filter value (e.g., "待审核")
            
        Returns:
            Full Airtable URL
        """
        base_id = os.getenv("AIRTABLE_BASE_ID")
        table_id = os.getenv("AIRTABLE_CONTENT_TABLE_ID", "tblContentHub")
        view_id = os.getenv("AIRTABLE_GRID_VIEW_ID", "viwGridView")
        
        link = f"https://airtable.com/{base_id}/{table_id}/{view_id}"
        
        if filter:
            # URL-encode filter parameter
            from urllib.parse import quote
            link += f"?filter={quote(filter)}"
        
        return link
    
    def _notify_user(self, message: str):
        """
        Send notification to user (via OpenClaw chat)
        
        In production, this would integrate with OpenClaw's messaging system.
        For now, just print to console.
        """
        print(f"\n📢 Notification:\n{message}\n")
        # TODO: Integrate with OpenClaw notification API
