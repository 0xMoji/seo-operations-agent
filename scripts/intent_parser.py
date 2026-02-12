"""
Intent Parser

Natural language understanding for conversational commands.
Uses regex patterns and keyword matching to extract user intent.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Intent:
    """Parsed user intent"""
    type: str
    params: Dict[str, Any]
    confidence: float


class IntentParser:
    """Parse natural language commands into structured intents"""
    
    def __init__(self):
        # Intent patterns (regex + keywords)
        self.patterns = {
            "setup": [
                r"启动.*SEO.*自动化",
                r"初始化|配置|设置.*系统"
            ],
            "create_campaign": [
                r"启动.*计划",
                r"创建.*运营.*计划",
                r"为期\s*(\d+)\s*天",
                r"主题是?\s*(.+?)(?:，|,|$)",
                r"每天\s*(\d+)\s*篇"
            ],
            "add_keywords": [
                r"关键词.*加到.*词库",
                r"添加.*关键词",
                r"把这些关键词"
            ],
            "generate_content": [
                r"现在生成内容",
                r"生成\s*(\d+)?\s*篇?文章",
                r"立即生成"
            ],
            "status_query": [
                r"汇报.*进度",
                r"查看.*状态",
                r"统计.*数据",
                r"当前.*进展"
            ],
            "stop_campaign": [
                r"停止.*计划",
                r"暂停.*运营",
                r"结束.*SEO"
            ],
            "manual_trigger": [
                r"trigger_publish",
                r"手动发布",
                r"立即发布"
            ]
        }
    
    def parse(self, message: str) -> Intent:
        """
        Parse user message into intent
        
        Args:
            message: User's natural language input
            
        Returns:
            Intent object with type and extracted parameters
        """
        message = message.strip()
        
        # Try each intent pattern
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    params = self._extract_params(intent_type, message)
                    return Intent(
                        type=intent_type,
                        params=params,
                        confidence=0.9
                    )
        
        # Unknown intent
        return Intent(type="unknown", params={}, confidence=0.0)
    
    def _extract_params(self, intent_type: str, message: str) -> Dict[str, Any]:
        """Extract parameters based on intent type"""
        
        if intent_type == "create_campaign":
            return self._extract_campaign_params(message)
        
        elif intent_type == "add_keywords":
            return self._extract_keywords(message)
        
        elif intent_type == "generate_content":
            return self._extract_content_count(message)
        
        return {}
    
    def _extract_campaign_params(self, message: str) -> Dict[str, Any]:
        """Extract campaign creation parameters"""
        params = {}
        
        # Duration
        duration_match = re.search(r"为期\s*(\d+)\s*天", message)
        if duration_match:
            params["duration"] = int(duration_match.group(1))
        
        # Topic
        topic_match = re.search(r"主题是?\s*([^，,。]+)", message)
        if topic_match:
            topic = topic_match.group(1).strip()
            # Remove trailing words like "每天"
            topic = re.sub(r"每天.*$", "", topic).strip()
            params["topic"] = topic
        
        # Frequency
        freq_match = re.search(r"每天\s*(\d+)\s*篇", message)
        if freq_match:
            params["frequency"] = int(freq_match.group(1))
        else:
            params["frequency"] = 1  # Default
        
        return params
    
    def _extract_keywords(self, message: str) -> Dict[str, Any]:
        """Extract keyword list from message"""
        # Find content after "关键词" or ":"
        keyword_part = message
        
        if "：" in message:
            keyword_part = message.split("：", 1)[1]
        elif ":" in message:
            keyword_part = message.split(":", 1)[1]
        elif "加到词库里" in message:
            keyword_part = message.split("加到词库里", 1)[0]
            keyword_part = keyword_part.replace("把这些关键词", "").strip()
        
        # Split by common delimiters
        keywords = re.split(r"[,，、]", keyword_part)
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        
        return {"keywords": keywords}
    
    def _extract_content_count(self, message: str) -> Dict[str, Any]:
        """Extract number of articles to generate"""
        count_match = re.search(r"生成\s*(\d+)", message)
        
        if count_match:
            return {"count": int(count_match.group(1))}
        
        return {"count": 5}  # Default
