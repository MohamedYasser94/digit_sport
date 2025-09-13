import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from core.utils.telegram_services import TelegramBotService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test Telegram bot connection and send test message'

    def add_arguments(self, parser):
        parser.add_argument(
            '--send-test',
            action='store_true',
            help='Send a test message to the channel',
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing Telegram Bot Configuration...")
        self.stdout.write(f"Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
        self.stdout.write(f"Channel ID: {settings.TELEGRAM_CHANNEL_ID}")
        
        try:
            bot_service = TelegramBotService()
            
            # Test connection
            self.stdout.write("Testing bot connection...")
            result = asyncio.run(bot_service.test_connection())
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Connection successful!\n"
                        f"Bot: @{result['bot_username']}\n"
                        f"Channel: {result['channel_title']} ({result['channel_id']})"
                    )
                )
                
                if options['send_test']:
                    self.stdout.write("Sending test message...")
                    
                    # Send test message
                    test_post_data = {
                        'title': 'Test Message from Django',
                        'content': 'This is a test message to verify the Telegram bot integration is working correctly.',
                        'image_url': None,
                        'image_path': None
                    }
                    
                    send_result = asyncio.run(bot_service.send_post_to_channel(test_post_data))
                    
                    if send_result['success']:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Test message sent successfully! Message ID: {send_result['message_id']}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"❌ Failed to send test message: {send_result['error']}"
                            )
                        )
                        
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Connection failed: {result['error']}")
                )
                
                # Provide troubleshooting tips
                self.stdout.write("\n" + "="*50)
                self.stdout.write("TROUBLESHOOTING TIPS:")
                self.stdout.write("="*50)
                self.stdout.write("1. Make sure your bot token is correct")
                self.stdout.write("2. Check that the channel ID is correct (should start with -100 for supergroups)")
                self.stdout.write("3. Ensure the bot is added as an administrator to the channel")
                self.stdout.write("4. Verify the bot has permission to send messages")
                self.stdout.write("5. For private channels, use the numeric ID, not @username")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Unexpected error: {e}")
            )
            logger.error(f"Telegram bot test error: {e}")
