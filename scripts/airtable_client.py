"""
Airtable Client Module

Handles all interactions with Airtable API including schema management,
CRUD operations, and deep link generation.
"""

import os
import requests
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Campaign:
    """Campaign model matching Airtable schema"""
    plan_name: str
    start_date: date
    end_date: date
    frequency: int
    publish_time: str
    auto_approve: bool
    is_active: bool
    website_webhook_url: Optional[str] = None
    buffer_channels: List[str] = None
    
    def to_airtable(self) -> Dict[str, Any]:
        """Convert to Airtable API format"""
        return {
            "Plan Name": self.plan_name,
            "Start Date": self.start_date.isoformat(),
            "End Date": self.end_date.isoformat(),
            "Frequency": self.frequency,
            "Publish Time": self.publish_time,
            "Auto Approve": self.auto_approve,
            "Is Active": self.is_active,
            "Website Webhook URL": self.website_webhook_url or "",
            "Buffer Channels": self.buffer_channels or []
        }


class AirtableClient:
    """Client for Airtable API operations"""
    
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}" if self.base_id else None
        self.meta_api_url = "https://api.airtable.com/v0/meta"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Table names from config
        self.tables = {
            "campaigns": "Campaign_Settings",
            "keywords": "Keyword_Pool",
            "content": "Content_Hub"
        }
    
    def is_configured(self) -> bool:
        """Check if Airtable is properly configured"""
        return bool(self.api_key and self.base_id)
    
    def check_and_initialize_base(self) -> Dict[str, Any]:
        """
        Check if base exists and has required tables.
        If not, create base and tables automatically.
        
        Returns:
            Dict with status and base_id
        """
        if not self.api_key:
            return {"status": "error", "message": "AIRTABLE_API_KEY not set"}
        
        # If base_id exists, check if it's valid
        if self.base_id:
            try:
                # Try to get base schema
                base_info = self._get_base_schema()
                
                # Check if all required tables exist
                existing_tables = {table["name"] for table in base_info.get("tables", [])}
                required_tables = set(self.tables.values())
                
                if required_tables.issubset(existing_tables):
                    return {
                        "status": "exists",
                        "message": "Base and tables already configured",
                        "base_id": self.base_id
                    }
                else:
                    missing = required_tables - existing_tables
                    # Create missing tables
                    self._create_missing_tables(list(missing))
                    return {
                        "status": "updated",
                        "message": f"Created missing tables: {', '.join(missing)}",
                        "base_id": self.base_id
                    }
            except Exception as e:
                print(f"Base check failed: {e}")
        
        # Base doesn't exist or is invalid, create new one
        return self._create_base_with_schema()
    
    def _get_base_schema(self) -> Dict[str, Any]:
        """Get base schema using Metadata API"""
        url = f"{self.meta_api_url}/bases/{self.base_id}/tables"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def _create_base_with_schema(self) -> Dict[str, Any]:
        """
        Create new Airtable base with complete schema
        
        Returns:
            Dict with status and new base_id
        """
        # Create base
        workspace_id = self._get_first_workspace_id()
        
        create_url = f"{self.meta_api_url}/bases"
        payload = {
            "name": "SEO Content Hub",
            "workspaceId": workspace_id,
            "tables": self._build_schema_definition()
        }
        
        response = requests.post(create_url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        result = response.json()
        new_base_id = result["id"]
        
        # Update instance variables
        self.base_id = new_base_id
        self.base_url = f"https://api.airtable.com/v0/{new_base_id}"
        
        return {
            "status": "created",
            "message": "Successfully created new base with all tables",
            "base_id": new_base_id,
            "base_url": f"https://airtable.com/{new_base_id}"
        }
    
    def _get_first_workspace_id(self) -> str:
        """Get first available workspace ID"""
        url = f"{self.meta_api_url}/bases"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        bases = response.json().get("bases", [])
        if bases:
            # Get workspace from first base
            first_base_id = bases[0]["id"]
            base_detail_url = f"{self.meta_api_url}/bases/{first_base_id}"
            detail_response = requests.get(base_detail_url, headers=self.headers)
            detail_response.raise_for_status()
            return detail_response.json()["workspaceId"]
        
        # Fallback: create in default workspace (empty string works for personal workspace)
        return ""
    
    def _build_schema_definition(self) -> List[Dict[str, Any]]:
        """Build complete schema definition for all 3 tables"""
        return [
            {
                "name": "Campaign_Settings",
                "description": "SEO campaign configuration and scheduling",
                "fields": [
                    {"name": "Plan Name", "type": "singleLineText"},
                    {"name": "Start Date", "type": "date"},
                    {"name": "End Date", "type": "date"},
                    {"name": "Frequency", "type": "number", "options": {"precision": 0}},
                    {"name": "Publish Time", "type": "singleLineText"},
                    {"name": "Auto Approve", "type": "checkbox"},
                    {"name": "Is Active", "type": "checkbox"},
                    {"name": "Website Webhook URL", "type": "url"},
                    {
                        "name": "Buffer Channels",
                        "type": "multipleSelects",
                        "options": {
                            "choices": [
                                {"name": "twitter"},
                                {"name": "linkedin"},
                                {"name": "bluesky"}
                            ]
                        }
                    }
                ]
            },
            {
                "name": "Keyword_Pool",
                "description": "Keyword library for content generation",
                "fields": [
                    {"name": "Keyword", "type": "singleLineText"},
                    {
                        "name": "Status",
                        "type": "singleSelect",
                        "options": {
                            "choices": [
                                {"name": "Available"},
                                {"name": "Used"},
                                {"name": "Deprecated"}
                            ]
                        }
                    },
                    {"name": "Knowledge", "type": "multilineText"},
                    {
                        "name": "Collection Status",
                        "type": "singleSelect",
                        "options": {
                            "choices": [
                                {"name": "Ready"},
                                {"name": "Needs Knowledge"},
                                {"name": "Awaiting Answers"},
                                {"name": "Skipped"}
                            ]
                        }
                    },
                    {"name": "Pending Questions", "type": "multilineText"}
                ]
            },
            {
                "name": "Content_Hub",
                "description": "Generated content library with multi-platform publishing workflow",
                "fields": [
                    {"name": "Title", "type": "singleLineText"},
                    {"name": "Body", "type": "multilineText"},
                    {"name": "SEO Metadata", "type": "multilineText"},
                    {"name": "Social Snippet", "type": "multilineText"},
                    {"name": "Images", "type": "multipleAttachments"},
                    {"name": "Image Metadata", "type": "multilineText"},
                    {
                        "name": "Status",
                        "type": "singleSelect",
                        "options": {
                            "choices": [
                                {"name": "Pending"},
                                {"name": "Approved"},
                                {"name": "Published"}
                            ]
                        }
                    },
                    {
                        "name": "Platform",
                        "type": "multipleSelects",
                        "options": {
                            "choices": [
                                {"name": "X (Twitter)"},
                                {"name": "LinkedIn"},
                                {"name": "Website"}
                            ]
                        }
                    },
                    {"name": "Scheduled Time", "type": "dateTime"},
                    {"name": "Next to Publish", "type": "checkbox"},
                    {"name": "Live URL", "type": "url"},
                    {"name": "Published At", "type": "dateTime"}
                ]
            }
        ]
    
    def _create_missing_tables(self, table_names: List[str]):
        """Create missing tables in existing base"""
        schema = self._build_schema_definition()
        
        for table_def in schema:
            if table_def["name"] in table_names:
                url = f"{self.meta_api_url}/bases/{self.base_id}/tables"
                
                response = requests.post(url, json=table_def, headers=self.headers)
                response.raise_for_status()
                
                print(f"✅ Created table: {table_def['name']}")

    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """
        Create new campaign record
        
        Returns:
            Record ID
        """
        url = f"{self.base_url}/{self.tables['campaigns']}"
        
        payload = {
            "fields": campaign_data
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()["id"]
    
    def get_active_campaigns(self) -> List[Dict[str, Any]]:
        """Get all active campaigns"""
        url = f"{self.base_url}/{self.tables['campaigns']}"
        params = {
            "filterByFormula": "{Is Active} = TRUE()"
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        records = response.json().get("records", [])
        return [self._parse_campaign_record(r) for r in records]
    
    def deactivate_all_campaigns(self) -> int:
        """Deactivate all campaigns"""
        campaigns = self.get_active_campaigns()
        
        for campaign in campaigns:
            self.update_record(
                self.tables['campaigns'],
                campaign['id'],
                {"Is Active": False}
            )
        
        return len(campaigns)
    
    def add_keywords(self, keywords: List[str]) -> int:
        """Batch add keywords to pool"""
        url = f"{self.base_url}/{self.tables['keywords']}"
        
        records = [
            {
                "fields": {
                    "Keyword": kw,
                    "Status": "Available",
                    "Collection Status": "Needs Knowledge"
                }
            }
            for kw in keywords
        ]
        
        # Airtable supports max 10 records per request
        created_count = 0
        for i in range(0, len(records), 10):
            batch = records[i:i+10]
            payload = {"records": batch}
            
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            created_count += len(response.json().get("records", []))
        
        return created_count
    
    def get_available_keyword(self, campaign: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get next available keyword with its knowledge and collection status.
        
        Returns:
            Dict with 'keyword', 'knowledge', 'collection_status', and 'record_id' fields, or None
        """
        url = f"{self.base_url}/{self.tables['keywords']}"
        
        params = {
            "filterByFormula": "{Status} = 'Available'",
            "maxRecords": 1
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        records = response.json().get("records", [])
        
        if records:
            fields = records[0]["fields"]
            return {
                "keyword": fields.get("Keyword"),
                "knowledge": fields.get("Knowledge", ""),
                "collection_status": fields.get("Collection Status", "Needs Knowledge"),
                "record_id": records[0]["id"]
            }
        
        return None
    
    def update_keyword_knowledge(self, record_id: str, knowledge: str):
        """Update the knowledge field for a specific keyword record."""
        self.update_record(self.tables['keywords'], record_id, {"Knowledge": knowledge})
    
    def create_content(self, content: Dict[str, Any]) -> str:
        """Create content record with support for multiple images"""
        url = f"{self.base_url}/{self.tables['content']}"
        
        # Prepare image attachments
        images = []
        if content.get("images"):
            for img in content["images"]:
                if isinstance(img, dict) and "url" in img:
                    images.append({"url": img["url"]})
                elif isinstance(img, str):
                    images.append({"url": img})
        
        payload = {
            "fields": {
                "Title": content["title"],
                "Body": content["body"],
                "SEO Metadata": content.get("seo_metadata", {}),
                "Social Snippet": content.get("social_snippet", ""),
                "Images": images,
                "Image Metadata": content.get("image_metadata", "[]"),
                "Status": content.get("status", "Pending"),
                "Platform": content.get("platforms", []),
                "Scheduled Time": content.get("scheduled_time", "")
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()["id"]
    
    def update_status(self, record_id: str, status: str):
        """Update content status"""
        self.update_record(self.tables['content'], record_id, {"Status": status})
    
    def count_records(self, status: str) -> int:
        """Count records by status"""
        url = f"{self.base_url}/{self.tables['content']}"
        params = {
            "filterByFormula": f"{{Status}} = '{status}'"
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        return len(response.json().get("records", []))
    
    def count_pending_content(self, channel: str) -> int:
        """Count pending/approved content for a specific channel"""
        # Simplified: count all pending + approved
        # In production, would filter by channel
        pending = self.count_records("Pending")
        approved = self.count_records("Approved")
        return pending + approved
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, int]:
        """Get statistical overview of campaign"""
        return {
            "total_keywords": self._count_table_records(self.tables['keywords']),
            "used_keywords": self._count_by_formula(
                self.tables['keywords'],
                "{Status} = 'Used'"
            ),
            "pending_articles": self.count_records("Pending"),
            "approved_articles": self.count_records("Approved"),
            "published_articles": self.count_records("Published"),
            "today_published": self._count_published_today()
        }
    
    def update_record(self, table: str, record_id: str, fields: Dict[str, Any]):
        """Generic record update"""
        url = f"{self.base_url}/{table}/{record_id}"
        payload = {"fields": fields}
        
        response = requests.patch(url, json=payload, headers=self.headers)
        response.raise_for_status()
    
    def _parse_campaign_record(self, record: Dict) -> Dict[str, Any]:
        """Parse Airtable record to campaign dict"""
        fields = record["fields"]
        return {
            "id": record["id"],
            "plan_name": fields.get("Plan Name"),
            "start_date": datetime.fromisoformat(fields.get("Start Date")).date(),
            "end_date": datetime.fromisoformat(fields.get("End Date")).date(),
            "frequency": fields.get("Frequency"),
            "publish_time": fields.get("Publish Time"),
            "auto_approve": fields.get("Auto Approve", False),
            "website_webhook_url": fields.get("Website Webhook URL"),
            "buffer_channels": fields.get("Buffer Channels", [])
        }
    
    def _count_table_records(self, table: str) -> int:
        """Count all records in table"""
        url = f"{self.base_url}/{table}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return len(response.json().get("records", []))
    
    def _count_by_formula(self, table: str, formula: str) -> int:
        """Count records matching formula"""
        url = f"{self.base_url}/{table}"
        params = {"filterByFormula": formula}
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return len(response.json().get("records", []))
    
    def _count_published_today(self) -> int:
        """Count articles published today"""
        today = date.today().isoformat()
        formula = f"AND({{Status}} = 'Published', IS_SAME({{Published At}}, '{today}', 'day'))"
        return self._count_by_formula(self.tables['content'], formula)
    
    def get_keyword_awaiting_answers(self) -> Optional[Dict[str, Any]]:
        """
        Get keyword that is awaiting user answers.
        
        Returns:
            Dict with keyword data or None
        """
        url = f"{self.base_url}/{self.tables['keywords']}"
        
        params = {
            "filterByFormula": "{Collection Status} = 'Awaiting Answers'",
            "maxRecords": 1
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        records = response.json().get("records", [])
        
        if records:
            fields = records[0]["fields"]
            return {
                "keyword": fields.get("Keyword"),
                "knowledge": fields.get("Knowledge", ""),
                "pending_questions": fields.get("Pending Questions", ""),
                "record_id": records[0]["id"]
            }
        
        return None
    
    def update_keyword_collection_status(
        self, 
        record_id: str, 
        status: str,
        pending_questions: Optional[str] = None,
        knowledge: Optional[str] = None
    ):
        """Update collection status and related fields for a keyword"""
        fields = {"Collection Status": status}
        
        if pending_questions is not None:
            fields["Pending Questions"] = pending_questions
        
        if knowledge is not None:
            fields["Knowledge"] = knowledge
        
        self.update_record(self.tables['keywords'], record_id, fields)

