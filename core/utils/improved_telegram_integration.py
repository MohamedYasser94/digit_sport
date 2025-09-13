import asyncio
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from core.utils.telegram_services import TelegramBotService

logger = logging.getLogger(__name__)

class ImprovedTelegramIntegration:
    """
    Improved Telegram integration for blog articles with better error handling
    """
    
    def __init__(self):
        self.bot_service = TelegramBotService()
        self.enabled = self._check_telegram_config()
    
    def _check_telegram_config(self) -> bool:
        """Check if Telegram is properly configured"""
        try:
            if not hasattr(settings, 'TELEGRAM_BOT_TOKEN') or not settings.TELEGRAM_BOT_TOKEN:
                logger.warning("TELEGRAM_BOT_TOKEN not configured")
                return False
            
            if not hasattr(settings, 'TELEGRAM_CHANNEL_ID') or not settings.TELEGRAM_CHANNEL_ID:
                logger.warning("TELEGRAM_CHANNEL_ID not configured")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error checking Telegram config: {e}")
            return False
    
    def _prepare_image_url(self, image_url: str, request=None) -> str:
        """Convert relative URLs to absolute URLs"""
        if not image_url:
            return None
            
        if image_url.startswith('http'):
            return image_url
            
        if image_url.startswith('/'):
            try:
                if request:
                    # Use request to build absolute URI
                    return request.build_absolute_uri(image_url)
                else:
                    # Fallback to settings or default
                    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000').rstrip('/')
                    return base_url + image_url
            except Exception as e:
                logger.error(f"Error building absolute URL: {e}")
                return None
        
        return image_url
    
    def _clean_content(self, content: str, max_length: int = 3900) -> str:
        """Clean HTML content for Telegram"""
        if not content:
            return ""
            
        # Strip HTML tags
        clean_content = strip_tags(content)
        
        # Truncate if too long
        if len(clean_content) > max_length:
            clean_content = clean_content[:max_length] + "..."
            
        return clean_content
    
    def _format_telegram_message(self, title: str, content: str) -> str:
        """Format message for Telegram with Markdown"""
        clean_content = self._clean_content(content)
        
        # Escape special Markdown characters in title and content
        title = title.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        clean_content = clean_content.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        
        message = f"*{title}*\n\n{clean_content}"
        
        # Ensure message is not too long
        if len(message) > 4000:
            message = message[:3950] + "...\n\n[Message truncated]"
            
        return message
    
    async def send_article_async(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send article to Telegram channel (async)"""
        if not self.enabled:
            return {
                'success': False,
                'error': 'Telegram not properly configured'
            }
        
        try:
            title = article_data.get('title', 'No Title')
            content = article_data.get('content', '')
            image_url = article_data.get('image_url')
            request = article_data.get('request')
            
            # Prepare image URL
            if image_url:
                image_url = self._prepare_image_url(image_url, request)
            
            # Prepare post data
            post_data = {
                'title': title,
                'content': content,
                'image_url': image_url,
                'image_path': article_data.get('image_path')
            }
            
            # Send to Telegram
            result = await self.bot_service.send_post_to_channel(post_data)
            
            if result['success']:
                logger.info(f"Successfully sent article to Telegram: {title}")
            else:
                logger.error(f"Failed to send article to Telegram: {result['error']}")
                
            return result
            
        except Exception as e:
            error_msg = f"Error sending article to Telegram: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def send_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send article to Telegram channel (sync wrapper)"""
        try:
            return asyncio.run(self.send_article_async(article_data))
        except Exception as e:
            error_msg = f"Error in sync wrapper: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Telegram connection"""
        if not self.enabled:
            return {
                'success': False,
                'error': 'Telegram not properly configured'
            }
        
        try:
            return asyncio.run(self.bot_service.test_connection())
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Convenience function for easy integration
def send_blog_article_to_telegram(article_object, request=None) -> Dict[str, Any]:
    """
    Convenience function to send a blog article to Telegram
    
    Args:
        article_object: BlogArticle instance
        request: Django request object (optional, for building absolute URLs)
    
    Returns:
        Dict with success status and details
    """
    telegram = ImprovedTelegramIntegration()
    
    # Prepare article data
    article_data = {
        'title': article_object.title,
        'content': getattr(article_object, 'body', '') or getattr(article_object, 'content', ''),
        'request': request
    }
    
    # Add image URL if available
    if hasattr(article_object, 'image') and article_object.image:
        try:
            article_data['image_url'] = article_object.image.url
        except:
            pass
    
    # Add image path if available
    if hasattr(article_object, 'image_path') and article_object.image_path:
        article_data['image_path'] = article_object.image_path
    
    return telegram.send_article(article_data)

# Simple test function
def test_telegram_setup() -> None:
    """Simple test function to check Telegram setup"""
    telegram = ImprovedTelegramIntegration()
    
    print(f"Telegram enabled: {telegram.enabled}")
    
    if telegram.enabled:
        result = telegram.test_connection()
        if result['success']:
            print(f"✅ Connected to bot: @{result['bot_username']}")
            print(f"✅ Channel: {result.get('channel_title', 'Unknown')}")
        else:
            print(f"❌ Connection failed: {result['error']}")
            print("\nMake sure:")
            print("1. The bot @Jawla_bot is added to your channel as an administrator")
            print("2. The bot has permission to post messages")
            print("3. The TELEGRAM_CHAT_ID in your .env file is correct")
    else:
        print("❌ Telegram not properly configured")
        print("Check your .env file for TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
