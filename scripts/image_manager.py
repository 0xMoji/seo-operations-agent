"""
Image Management Module

Handles multi-source image acquisition and platform-specific formatting:
- AI generation (DALL-E, Stable Diffusion, etc.)
- Unsplash search
- Manual upload
- Image position tracking for different platforms
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass
from pathlib import Path


ImagePurpose = Literal["cover", "inline", "social", "thumbnail"]
ImageSource = Literal["dall-e-3", "dall-e-2", "stable-diffusion", "unsplash", "manual", "user-upload"]


@dataclass
class ImageMetadata:
    """Metadata for a single image"""
    filename: str
    purpose: ImagePurpose
    platforms: List[str]
    position: str
    alt_text: str
    source: ImageSource
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "purpose": self.purpose,
            "platforms": self.platforms,
            "position": self.position,
            "alt_text": self.alt_text,
            "source": self.source,
            "url": self.url
        }


class ImageManager:
    """Manages image acquisition from multiple sources"""
    
    def __init__(self):
        # AI Image Generation
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        
        # Stock Photos
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        # Configuration
        self.default_image_model = os.getenv("IMAGE_GENERATION_MODEL", "dall-e-3")
        self.temp_dir = Path("./temp_images")
        self.temp_dir.mkdir(exist_ok=True)
    
    def generate_images_for_content(
        self,
        keyword: str,
        title: str,
        platforms: List[str],
        num_images: int = 1,
        purposes: Optional[List[ImagePurpose]] = None
    ) -> List[ImageMetadata]:
        """
        Generate or fetch images for content across platforms.
        
        Args:
            keyword: Content keyword for image search/generation
            title: Article title for context
            platforms: Target platforms (determines image requirements)
            num_images: Number of images to generate/fetch
            purposes: Specific purposes for each image
            
        Returns:
            List of ImageMetadata objects
        """
        if purposes is None:
            purposes = self._determine_purposes(platforms, num_images)
        
        images = []
        
        for i, purpose in enumerate(purposes):
            try:
                if purpose == "cover":
                    image = self._generate_cover_image(keyword, title, platforms)
                elif purpose == "social":
                    image = self._generate_social_image(keyword, title)
                else:
                    image = self._fetch_inline_image(keyword, i)
                
                if image:
                    images.append(image)
                    
            except Exception as e:
                print(f"Failed to generate {purpose} image: {e}")
        
        return images
    
    def _determine_purposes(self, platforms: List[str], num_images: int) -> List[ImagePurpose]:
        """Determine image purposes based on platforms"""
        purposes = ["cover"]  # Always need cover
        
        # Add social-specific image if posting to social media
        if any(p in platforms for p in ["X (Twitter)", "LinkedIn"]):
            purposes.append("social")
        
        # Add inline images for website
        if "Website" in platforms and num_images > len(purposes):
            remaining = num_images - len(purposes)
            purposes.extend(["inline"] * remaining)
        
        return purposes[:num_images]
    
    def _generate_cover_image(
        self,
        keyword: str,
        title: str,
        platforms: List[str]
    ) -> Optional[ImageMetadata]:
        """Generate or fetch cover image"""
        
        # Try AI generation first if configured
        if self.default_image_model.startswith("dall-e"):
            return self._generate_dalle_image(
                keyword, 
                title, 
                purpose="cover",
                platforms=platforms
            )
        elif self.default_image_model == "stable-diffusion":
            return self._generate_sd_image(
                keyword,
                title,
                purpose="cover",
                platforms=platforms
            )
        
        # Fallback to Unsplash
        return self._fetch_unsplash_image(keyword, purpose="cover", platforms=platforms)
    
    def _generate_social_image(
        self,
        keyword: str,
        title: str
    ) -> Optional[ImageMetadata]:
        """Generate social media optimized image"""
        
        # Social images work best with AI generation (custom text overlay)
        if self.openai_api_key:
            return self._generate_dalle_image(
                keyword,
                title,
                purpose="social",
                platforms=["X (Twitter)", "LinkedIn"],
                size="1024x1024"  # Square for social
            )
        
        return self._fetch_unsplash_image(
            keyword,
            purpose="social",
            platforms=["X (Twitter)", "LinkedIn"]
        )
    
    def _fetch_inline_image(
        self,
        keyword: str,
        index: int
    ) -> Optional[ImageMetadata]:
        """Fetch inline image (prefer stock photos for cost)"""
        
        return self._fetch_unsplash_image(
            keyword,
            purpose="inline",
            platforms=["Website"],
            position=f"after-paragraph-{index + 1}"
        )
    
    def _generate_dalle_image(
        self,
        keyword: str,
        title: str,
        purpose: ImagePurpose,
        platforms: List[str],
        size: str = "1792x1024",
        position: str = "featured"
    ) -> Optional[ImageMetadata]:
        """Generate image using DALL-E"""
        
        if not self.openai_api_key:
            return None
        
        # Build prompt based on purpose
        if purpose == "cover":
            prompt = f"Professional blog header image for article titled '{title}', modern and clean design, topic: {keyword}"
        elif purpose == "social":
            prompt = f"Eye-catching social media image for topic: {keyword}, vibrant and engaging"
        else:
            prompt = f"Illustration for {keyword}, professional and informative"
        
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.default_image_model,
            "prompt": prompt,
            "size": size,
            "quality": "standard",
            "n": 1
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            image_url = data["data"][0]["url"]
            
            # Download image
            filename = f"{purpose}_{keyword[:20].replace(' ', '_')}.png"
            image_path = self.temp_dir / filename
            
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            with open(image_path, "wb") as f:
                f.write(img_response.content)
            
            return ImageMetadata(
                filename=filename,
                purpose=purpose,
                platforms=platforms,
                position=position,
                alt_text=f"{purpose.capitalize()} image for {title}",
                source="dall-e-3",
                url=str(image_path)
            )
            
        except Exception as e:
            print(f"DALL-E generation failed: {e}")
            return None
    
    def _generate_sd_image(
        self,
        keyword: str,
        title: str,
        purpose: ImagePurpose,
        platforms: List[str]
    ) -> Optional[ImageMetadata]:
        """Generate image using Stable Diffusion API"""
        
        if not self.stability_api_key:
            return None
        
        # Placeholder for Stable Diffusion implementation
        # Users can extend this based on their SD API provider
        print("Stable Diffusion generation not yet implemented")
        return None
    
    def _fetch_unsplash_image(
        self,
        keyword: str,
        purpose: ImagePurpose,
        platforms: List[str],
        position: str = "featured"
    ) -> Optional[ImageMetadata]:
        """Fetch image from Unsplash"""
        
        if not self.unsplash_key:
            return None
        
        url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {self.unsplash_key}"
        }
        
        # Determine orientation based on purpose
        orientation = "landscape" if purpose in ["cover", "inline"] else "squarish"
        
        params = {
            "query": keyword,
            "per_page": 1,
            "orientation": orientation
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            results = response.json().get("results", [])
            if not results:
                return None
            
            photo = results[0]
            image_url = photo["urls"]["regular"]
            filename = f"{purpose}_{keyword[:20].replace(' ', '_')}_unsplash.jpg"
            
            return ImageMetadata(
                filename=filename,
                purpose=purpose,
                platforms=platforms,
                position=position,
                alt_text=photo.get("alt_description") or f"{purpose} image for {keyword}",
                source="unsplash",
                url=image_url
            )
            
        except Exception as e:
            print(f"Unsplash fetch failed: {e}")
            return None
    
    def add_manual_image(
        self,
        image_path: str,
        purpose: ImagePurpose,
        platforms: List[str],
        alt_text: str,
        position: str = "featured"
    ) -> ImageMetadata:
        """Add manually uploaded image"""
        
        filename = Path(image_path).name
        
        return ImageMetadata(
            filename=filename,
            purpose=purpose,
            platforms=platforms,
            position=position,
            alt_text=alt_text,
            source="user-upload",
            url=image_path
        )
    
    def format_for_platform(
        self,
        images: List[ImageMetadata],
        platform: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Format images for specific platform.
        
        Args:
            images: All images with metadata
            platform: Target platform
            body: Content body (for inline image insertion)
            
        Returns:
            Dict with platform-specific image data
        """
        
        platform_images = [img for img in images if platform in img.platforms]
        
        if platform == "Website":
            return self._format_for_website(platform_images, body)
        elif platform in ["X (Twitter)", "LinkedIn"]:
            return self._format_for_social(platform_images, platform)
        
        return {}
    
    def _format_for_website(
        self,
        images: List[ImageMetadata],
        body: str
    ) -> Dict[str, Any]:
        """Format images for website blog post"""
        
        cover = next((img for img in images if img.purpose == "cover"), None)
        inline_images = [img for img in images if img.purpose == "inline"]
        
        # Insert inline images into HTML body
        modified_body = body
        for img in sorted(inline_images, key=lambda x: x.position):
            if "after-paragraph-" in img.position:
                para_num = int(img.position.split("-")[-1])
                # Simple HTML insertion logic
                img_html = f'<img src="{img.url}" alt="{img.alt_text}" class="inline-image" />'
                # Would need more sophisticated HTML parsing in production
                modified_body += f"\n{img_html}"
        
        return {
            "featured_image": cover.url if cover else None,
            "featured_image_alt": cover.alt_text if cover else "",
            "body_with_images": modified_body,
            "all_images": [img.to_dict() for img in images]
        }
    
    def _format_for_social(
        self,
        images: List[ImageMetadata],
        platform: str
    ) -> Dict[str, Any]:
        """Format images for social media"""
        
        # Social platforms typically use one attached image
        social_img = next(
            (img for img in images if img.purpose == "social"),
            next((img for img in images if img.purpose == "cover"), None)
        )
        
        return {
            "media_url": social_img.url if social_img else None,
            "media_alt": social_img.alt_text if social_img else "",
            "platform": platform
        }
    
    def cleanup_temp_images(self):
        """Clean up temporary downloaded images"""
        for file in self.temp_dir.glob("*"):
            file.unlink()
