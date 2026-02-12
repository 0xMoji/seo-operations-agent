"""
Website Publisher Module

Handles direct publishing to user's website via flexible API integration.
Supports multiple authentication methods and content formats.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass


AuthMethod = Literal["api_key", "bearer", "basic", "oauth", "none"]


@dataclass
class WebsiteConfig:
    """Website API configuration"""
    endpoint_url: str
    auth_method: AuthMethod
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    oauth_token: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None


class WebsitePublisher:
    """Publishes content directly to user's website"""
    
    def __init__(self, config: Optional[WebsiteConfig] = None):
        """
        Initialize publisher with configuration.
        
        Args:
            config: Website configuration (if None, loads from env)
        """
        self.config = config or self._load_from_env()
    
    def _load_from_env(self) -> WebsiteConfig:
        """Load configuration from environment variables"""
        
        return WebsiteConfig(
            endpoint_url=os.getenv("WEBSITE_API_ENDPOINT", ""),
            auth_method=os.getenv("WEBSITE_AUTH_METHOD", "api_key"),
            api_key=os.getenv("WEBSITE_API_KEY"),
            username=os.getenv("WEBSITE_USERNAME"),
            password=os.getenv("WEBSITE_PASSWORD"),
            oauth_token=os.getenv("WEBSITE_OAUTH_TOKEN"),
            custom_headers=json.loads(os.getenv("WEBSITE_CUSTOM_HEADERS", "{}"))
        )
    
    def publish(
        self,
        content: Dict[str, Any],
        images: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Publish content to website.
        
        Args:
            content: Content data (title, body, metadata, etc.)
            images: Image data formatted for website
            
        Returns:
            Response with status and live URL
        """
        if not self.config.endpoint_url:
            return {
                "status": "error",
                "message": "No website endpoint configured"
            }
        
        # Build request payload
        payload = self._build_payload(content, images)
        
        # Build headers with authentication
        headers = self._build_headers()
        
        try:
            response = requests.post(
                self.config.endpoint_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "status": "success",
                "live_url": result.get("url") or result.get("permalink") or result.get("link"),
                "post_id": result.get("id"),
                "message": "Successfully published to website"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Publishing failed: {str(e)}"
            }
    
    def _build_payload(
        self,
        content: Dict[str, Any],
        images: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build API payload from content and images.
        
        This is a generic structure - users may need to customize
        based on their website's API requirements.
        """
        
        payload = {
            "title": content.get("title"),
            "content": content.get("body"),
            "status": "publish",  # or "draft" based on preferences
        }
        
        # Add SEO metadata if present
        if content.get("seo_metadata"):
            metadata = json.loads(content["seo_metadata"]) if isinstance(content["seo_metadata"], str) else content["seo_metadata"]
            payload["slug"] = metadata.get("slug")
            payload["meta_description"] = metadata.get("description")
            payload["excerpt"] = metadata.get("description")
        
        # Add images if present
        if images:
            if images.get("featured_image"):
                payload["featured_media_url"] = images["featured_image"]
            
            # Some APIs support body_with_images directly
            if images.get("body_with_images"):
                payload["content"] = images["body_with_images"]
        
        return payload
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-SEO-Agent/2.0"
        }
        
        # Add custom headers if configured
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)
        
        # Add authentication based on method
        if self.config.auth_method == "api_key":
            if self.config.api_key:
                headers["X-API-Key"] = self.config.api_key
        
        elif self.config.auth_method == "bearer":
            if self.config.oauth_token:
                headers["Authorization"] = f"Bearer {self.config.oauth_token}"
        
        elif self.config.auth_method == "basic":
            if self.config.username and self.config.password:
                import base64
                credentials = f"{self.config.username}:{self.config.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
        
        # "none" and "oauth" don't modify headers here
        
        return headers
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test website API connection.
        
        Returns:
            Status dict
        """
        if not self.config.endpoint_url:
            return {
                "status": "error",
                "message": "No endpoint configured"
            }
        
        try:
            # Try a simple GET request to check connectivity
            response = requests.get(
                self.config.endpoint_url,
                headers=self._build_headers(),
                timeout=10
            )
            
            return {
                "status": "success" if response.status_code < 500 else "error",
                "message": f"Connected (HTTP {response.status_code})"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
    
    @classmethod
    def configure_interactively(cls, agent_context):
        """
        Interactive configuration flow with user.
        
        This should be called by the main skill when user wants to
        set up website publishing.
        
        Args:
            agent_context: Agent context with conversation ability
            
        Returns:
            WebsiteConfig object
        """
        
        # This is a template - actual implementation would use
        # the agent's conversation capabilities
        
        config_questions = """
I'll help you set up direct website publishing. I need a few details:

1. **API Endpoint URL**: The full URL where I should POST new articles
   Example: `https://yoursite.com/wp-json/wp/v2/posts`

2. **Authentication Method**: How should I authenticate?
   - `api_key`: Custom API key header
   - `bearer`: OAuth bearer token
   - `basic`: HTTP basic auth (username/password)
   - `none`: No authentication

3. **Credentials**: Based on auth method above

Please provide these details, and I'll test the connection.
"""
        
        # Agent would ask user and parse responses
        # For now, return a placeholder
        return None


def setup_website_publishing_guide() -> str:
    """
    Returns a guide for users to set up website publishing.
    """
    
    return """
# Website Direct Publishing Setup

## Environment Variables

Add these to your `.env` file:

```bash
# Required
WEBSITE_API_ENDPOINT=https://yoursite.com/api/posts

# Authentication (choose one method)
WEBSITE_AUTH_METHOD=api_key  # Options: api_key, bearer, basic, oauth, none

# For api_key method:
WEBSITE_API_KEY=your_api_key_here

# For bearer method:
WEBSITE_OAUTH_TOKEN=your_oauth_token_here

# For basic method:
WEBSITE_USERNAME=your_username
WEBSITE_PASSWORD=your_password

# Optional custom headers (JSON format)
WEBSITE_CUSTOM_HEADERS={"X-Custom-Header": "value"}
```

## Common Platforms

### WordPress (REST API)
```bash
WEBSITE_API_ENDPOINT=https://yoursite.com/wp-json/wp/v2/posts
WEBSITE_AUTH_METHOD=basic
WEBSITE_USERNAME=your_wp_username
WEBSITE_PASSWORD=your_application_password  # Generate in WP admin
```

### Strapi CMS
```bash
WEBSITE_API_ENDPOINT=https://yoursite.com/api/articles
WEBSITE_AUTH_METHOD=bearer
WEBSITE_OAUTH_TOKEN=your_strapi_api_token
```

### Custom API
```bash
WEBSITE_API_ENDPOINT=https://api.yoursite.com/v1/blog/posts
WEBSITE_AUTH_METHOD=api_key
WEBSITE_API_KEY=your_secret_key
```

## Testing

After configuration, test with:
```python
from website_publisher import WebsitePublisher

publisher = WebsitePublisher()
result = publisher.test_connection()
print(result)
```

## Payload Format

The publisher sends this JSON structure:

```json
{
  "title": "Article Title",
  "content": "<p>HTML content...</p>",
  "slug": "article-slug",
  "status": "publish",
  "meta_description": "SEO description",
  "featured_media_url": "https://image-url.com/image.jpg"
}
```

Customize `_build_payload()` if your API expects different fields.
"""
