import asyncio
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send scheduled Telegram posts to channel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test connection only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send all pending posts regardless of schedule',
        )

    def handle(self, *args, **options):
        telegram_service = TelegramService()

        if options['test']:
            # Test connection
            result = asyncio.run(telegram_service.test_connection())
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Connection successful!\n"
                        f"Bot: @{result['bot_username']}\n"
                        f"Channel: {result['channel_title']} ({result['channel_id']})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Connection failed: {result['error']}")
                )
            return

        # Get posts to send
        now = timezone.now()
        if options['force']:
            posts = TelegramPost.objects.filter(sent=False)
        else:
            posts = TelegramPost.objects.filter(
                sent=False,
                scheduled_time__lte=now
            )

        if not posts.exists():
            self.stdout.write("No posts to send.")
            return

        self.stdout.write(f"Sending {posts.count()} posts...")

        for post in posts:
            try:
                # Prepare image path
                image_path = None
                image_url = None

                if post.image:
                    image_path = post.image.path
                elif post.image_url:
                    image_url = post.image_url

                # Send post
                result = asyncio.run(
                    telegram_service.send_article_to_channel(
                        title=post.title,
                        content=post.content,
                        image_path=image_path,
                        image_url=image_url
                    )
                )

                if result['success']:
                    # Update post as sent
                    post.sent = True
                    post.sent_at = timezone.now()
                    post.telegram_message_id = result['message_id']
                    post.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Sent: {post.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed to send '{post.title}': {result['error']}")
                    )

            except Exception as e:
                logger.error(f"Error sending post {post.id}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"❌ Error sending '{post.title}': {e}")
                )
