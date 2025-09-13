import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Get information about Telegram channels and groups the bot has access to'

    def handle(self, *args, **options):
        self.stdout.write("Getting Telegram channel information...")
        self.stdout.write(f"Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        
        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            
            # Get bot info
            self.stdout.write("Getting bot information...")
            bot_info = asyncio.run(bot.get_me())
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Bot Info:\n"
                    f"  Name: {bot_info.first_name}\n"
                    f"  Username: @{bot_info.username}\n"
                    f"  ID: {bot_info.id}"
                )
            )
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write("SETUP INSTRUCTIONS:")
            self.stdout.write("="*60)
            self.stdout.write("1. Add the bot @{} to your Telegram channel as an administrator".format(bot_info.username))
            self.stdout.write("2. Give the bot the following permissions:")
            self.stdout.write("   - Post messages")
            self.stdout.write("   - Edit messages")
            self.stdout.write("   - Delete messages")
            self.stdout.write("3. To get the channel ID, follow these steps:")
            self.stdout.write("   a) Forward a message from the channel to @userinfobot")
            self.stdout.write("   b) The bot will show the channel ID")
            self.stdout.write("   c) For supergroups/channels, the ID should start with -100")
            self.stdout.write("4. Update your .env file with the correct TELEGRAM_CHAT_ID")
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write("ALTERNATIVE METHOD TO GET CHANNEL ID:")
            self.stdout.write("="*60)
            self.stdout.write("1. Open Telegram Web (web.telegram.org)")
            self.stdout.write("2. Go to your channel")
            self.stdout.write("3. Look at the URL: the number after 'c/' is your channel ID")
            self.stdout.write("4. Add -100 prefix to it (e.g., if URL shows c/123456789, use -100123456789)")
            
            # Try some common variations if user provides a channel username
            self.stdout.write("\n" + "="*60)
            self.stdout.write("TESTING COMMON ID FORMATS:")
            self.stdout.write("="*60)
            
            current_id = settings.TELEGRAM_CHANNEL_ID
            test_ids = []
            
            # If it's a string starting with @, try to resolve it
            if isinstance(current_id, str) and current_id.startswith('@'):
                test_ids.append(current_id)
            
            # If it's a number, try different formats
            if str(current_id).replace('-', '').isdigit():
                base_id = str(current_id).replace('-100', '').replace('-', '')
                test_ids.extend([
                    f"-100{base_id}",
                    f"-{base_id}",
                    base_id,
                    int(base_id) if base_id.isdigit() else None
                ])
            
            # Remove duplicates and None values
            test_ids = list(set([id for id in test_ids if id is not None]))
            
            for test_id in test_ids:
                try:
                    self.stdout.write(f"Testing ID: {test_id}")
                    chat_info = asyncio.run(bot.get_chat(chat_id=test_id))
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ FOUND! Channel ID: {test_id}\n"
                            f"  Title: {chat_info.title}\n"
                            f"  Type: {chat_info.type}\n"
                            f"  ID: {chat_info.id}"
                        )
                    )
                    
                    self.stdout.write(f"\nUpdate your .env file:")
                    self.stdout.write(f"TELEGRAM_CHAT_ID={chat_info.id}")
                    break
                    
                except TelegramError as e:
                    self.stdout.write(f"  ❌ Failed: {e}")
                except Exception as e:
                    self.stdout.write(f"  ❌ Error: {e}")
            else:
                self.stdout.write(self.style.WARNING(
                    "\n❌ Could not find a working channel ID with the current configuration."
                ))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Unexpected error: {e}")
            )
            logger.error(f"Telegram channel info error: {e}")
