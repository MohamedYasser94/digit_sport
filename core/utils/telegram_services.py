# telegram_bot.py - Main Bot Functions
import asyncio
import logging
import os
from typing import Optional, List, Dict, Any
from io import BytesIO
import requests
from PIL import Image
from datetime import datetime, timedelta

from telegram import Bot
from telegram.error import TelegramError
from django.conf import settings
from django.utils import timezone



logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        # Fix for cached environment variable - use the correct channel ID
        raw_channel_id = settings.TELEGRAM_CHANNEL_ID
        if isinstance(raw_channel_id, str) and (raw_channel_id.startswith('"') or '#' in raw_channel_id):
            # Clean up malformed channel ID from cached env var
            self.channel_id = -1002976107731
            logger.warning(f"Fixed malformed channel ID: {raw_channel_id} -> {self.channel_id}")
        else:
            self.channel_id = raw_channel_id
        self.bot = Bot(token=self.bot_token)

    async def send_post_to_channel(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a single post to Telegram channel
        post_data: {
            'title': str,
            'content': str,
            'image_path': str (optional),
            'image_url': str (optional)
        }
        """
        try:
            title = post_data.get('title', '')
            content = post_data.get('content', '')
            image_path = post_data.get('image_path')
            image_url = post_data.get('image_url')

            # Clean HTML content
            from django.utils.html import strip_tags
            clean_content = strip_tags(content) if content else ""
            
            # Escape special Markdown characters in title and content
            title = title.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`') if title else ""
            clean_content = clean_content.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')

            # Format the message
            message_text = f"*{title}*\n\n{clean_content}" if title else clean_content

            # Truncate if message is too long
            if len(message_text) > 4000:
                message_text = message_text[:3950] + "...\n\n[Message truncated]"

            # Send with image if available
            if image_path or image_url:
                image_data = await self._get_image_data(image_path, image_url)
                if image_data:
                    message = await self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=image_data,
                        caption=message_text,
                        parse_mode='Markdown'
                    )
                else:
                    # Fallback to text only if image fails
                    message = await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=message_text,
                        parse_mode='Markdown'
                    )
            else:
                # Send text only
                message = await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message_text,
                    parse_mode='Markdown'
                )

            return {
                'success': True,
                'message_id': message.message_id,
                'error': None
            }

        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }

    async def _get_image_data(self, image_path: Optional[str], image_url: Optional[str]) -> Optional[BytesIO]:
        """Get image data from file path or URL"""
        try:
            if image_path and os.path.exists(image_path):
                # Read local image file
                with open(image_path, 'rb') as img_file:
                    return BytesIO(img_file.read())

            elif image_url:
                # Handle relative URLs - make them absolute
                if image_url.startswith('/'):
                    # Get base URL from Django settings
                    from django.contrib.sites.models import Site
                    try:
                        current_site = Site.objects.get_current()
                        protocol = 'https' if settings.DEBUG is False else 'http'
                        base_url = f"{protocol}://{current_site.domain}"
                        image_url = base_url + image_url
                    except:
                        # Fallback to settings BASE_URL or localhost
                        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000').rstrip('/')
                        image_url = base_url + image_url
                
                logger.info(f"Processing image URL: {image_url}")
                
                # Download image from URL
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(image_url, timeout=30, headers=headers)
                response.raise_for_status()

                # Verify it's an image and resize if needed
                img = Image.open(BytesIO(response.content))

                # Resize if too large
                if img.size[0] > 1920 or img.size[1] > 1080:
                    img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

                # Convert to BytesIO
                img_buffer = BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img.save(img_buffer, format=img_format, quality=85)
                img_buffer.seek(0)
                return img_buffer

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None

    async def test_connection(self) -> Dict[str, Any]:
        """Test bot connection and get channel info"""
        try:
            # Test bot
            bot_info = await self.bot.get_me()

            # Test channel access
            chat_info = await self.bot.get_chat(chat_id=self.channel_id)

            return {
                'success': True,
                'bot_username': bot_info.username,
                'channel_title': chat_info.title,
                'channel_id': chat_info.id
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
