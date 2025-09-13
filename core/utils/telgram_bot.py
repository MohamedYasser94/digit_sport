# telegram_functions.py - Main Functions for Bot Operations
import asyncio
from datetime import timedelta
from typing import Dict, Any, List

from django.db.models import QuerySet
from django.db.models.functions import datetime
from django.utils import timezone

from core.models.blog import BlogArticle
from .telegram_services import TelegramBotService
from ..models.blog import BlogArticle


def create_telegram_post(title: str, content: str, image_path: str = None,
                         image_url: str = None, scheduled_time: datetime = None) -> BlogArticle:
    """
    Create a new Telegram post

    Args:
        title: Post title
        content: Post content
        image_path: Path to local image file
        image_url: URL to image
        scheduled_time: When to send (default: now)

    Returns:
        BlogArticle object
    """
    if scheduled_time is None:
        scheduled_time = timezone.now()

    post = BlogArticle.objects.create(
        title=title,
        content=content,
        image_path=image_path,
        image_url=image_url,
        scheduled_time=scheduled_time
    )

    return post


def send_immediate_post(title: str, content: str, image_path: str = None,
                        image_url: str = None) -> Dict[str, Any]:
    """
    Create and immediately send a post to Telegram channel

    Returns:
        Dict with success status and details
    """
    try:
        bot_service = TelegramBotService()

        post_data = {
            'title': title,
            'content': content,
            'image_path': image_path,
            'image_url': image_url
        }

        # Send to Telegram
        result = asyncio.run(bot_service.send_post_to_channel(post_data))

        if result['success']:
            # Save to database
            post = BlogArticle.objects.create(
                title=title,
                content=content,
                image_path=image_path,
                image_url=image_url,
                sent=True,
                sent_at=timezone.now(),
                telegram_message_id=result['message_id']
            )

            return {
                'success': True,
                'post_id': post.id,
                'message_id': result['message_id'],
                'message': 'Post sent successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_scheduled_posts(force_all: bool = False) -> Dict[str, Any]:
    """
    Send all scheduled posts that are due

    Args:
        force_all: If True, send all pending posts regardless of schedule

    Returns:
        Dict with results
    """
    try:
        now = timezone.now()

        if force_all:
            posts = BlogArticle.objects.filter(sent=False)
        else:
            posts = BlogArticle.objects.filter(
                sent=False,
                scheduled_time__lte=now
            )

        if not posts.exists():
            return {
                'success': True,
                'sent_count': 0,
                'message': 'No posts to send'
            }

        bot_service = TelegramBotService()
        sent_count = 0
        failed_posts = []

        for post in posts:
            post_data = {
                'title': post.title,
                'content': post.body,
                'image_path': post.image_path,
                'image_url': post.image
            }

            result = asyncio.run(bot_service.send_post_to_channel(post_data))

            if result['success']:
                post.sent = True
                post.sent_at = timezone.now()
                post.telegram_message_id = result['message_id']
                post.save()
                sent_count += 1
            else:
                failed_posts.append({
                    'post_id': post.id,
                    'title': post.title,
                    'error': result['error']
                })

        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': len(failed_posts),
            'failed_posts': failed_posts,
            'message': f'Sent {sent_count} posts successfully'
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_pending_posts() -> QuerySet[BlogArticle, BlogArticle]:
    """Get all posts that haven't been sent yet"""
    return BlogArticle.objects.filter(sent=False).order_by('scheduled_time')


def get_sent_posts(limit: int = 50) -> QuerySet[BlogArticle, BlogArticle]:
    """Get recently sent posts"""
    return BlogArticle.objects.filter(sent=True).order_by('-sent_at')[:limit]


def delete_post(post_id: int) -> bool:
    """Delete a post by ID"""
    try:
        post = BlogArticle.objects.get(id=post_id)
        post.delete()
        return True
    except BlogArticle.DoesNotExist:
        return False


def test_bot_connection() -> Dict[str, Any]:
    """Test the bot connection"""
    bot_service = TelegramBotService()
    return asyncio.run(bot_service.test_connection())


def schedule_post(title: str, content: str, send_in_minutes: int,
                  image_path: str = None, image_url: str = None) -> BlogArticle:
    """
    Schedule a post to be sent after specified minutes

    Args:
        title: Post title
        content: Post content
        send_in_minutes: Minutes from now to send the post
        image_path: Path to local image
        image_url: URL to image

    Returns:
        BlogArticle object
    """
    scheduled_time = timezone.now() + timedelta(minutes=send_in_minutes)

    return create_telegram_post(
        title=title,
        content=content,
        image_path=image_path,
        image_url=image_url,
        scheduled_time=scheduled_time
    )


# Example usage file - usage_examples.py
"""
Example usage of the Telegram bot functions
"""



def example_usage():
    # Test connection first
    connection_test = test_bot_connection()
    if connection_test['success']:
        print(f"✅ Connected to bot: @{connection_test['bot_username']}")
        print(f"✅ Channel: {connection_test['channel_title']}")
    else:
        print(f"❌ Connection failed: {connection_test['error']}")
        return

    # Example 1: Send immediate post with image URL
    result1 = send_immediate_post(
        title="Breaking News: AI Revolution",
        content="Artificial Intelligence continues to transform industries worldwide. "
                "Latest developments show remarkable progress in automation and efficiency.",
        image_url="https://example.com/ai-image.jpg"
    )
    print(f"Immediate post result: {result1}")

    # Example 2: Send immediate post with local image
    result2 = send_immediate_post(
        title="Tech Update",
        content="Today's technology news includes major updates from leading companies.",
        image_path="/path/to/local/image.jpg"  # Make sure file exists
    )
    print(f"Local image post result: {result2}")

    # Example 3: Schedule post for later (30 minutes from now)
    scheduled_post = schedule_post(
        title="Scheduled Article",
        content="This post will be sent automatically in 30 minutes.",
        send_in_minutes=30,
        image_url="https://example.com/scheduled-image.jpg"
    )
    print(f"Scheduled post created: {scheduled_post.id}")

    # Example 4: Create post for specific time
    future_time = timezone.now() + timedelta(hours=2)
    post = create_telegram_post(
        title="Future Post",
        content="This will be sent in 2 hours.",
        scheduled_time=future_time
    )
    print(f"Future post created: {post.id}")

    # Example 5: Send all scheduled posts that are due
    send_result = send_scheduled_posts()
    print(f"Scheduled posts sent: {send_result}")

    # Example 6: Get pending posts
    pending = get_pending_posts()
    print(f"Pending posts: {len(pending)}")
    for post in pending[:5]:  # Show first 5
        print(f"  - {post.title} (scheduled: {post.scheduled_time})")


# management/commands/send_telegram_posts.py
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'Send scheduled Telegram posts'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true', help='Test connection only')
        parser.add_argument('--force', action='store_true', help='Send all pending posts')

    def handle(self, *args, **options):
        if options['test']:
            result = test_bot_connection()
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Connection successful!\n"
                        f"Bot: @{result['bot_username']}\n"
                        f"Channel: {result['channel_title']}"
                    )
                )
            else:
                self.stdout.write(self.style.ERROR(f"❌ Connection failed: {result['error']}"))
            return

        result = send_scheduled_posts(force_all=options['force'])

        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(f"✅ {result['message']}")
            )
            if result.get('failed_posts'):
                for failed in result['failed_posts']:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Failed: {failed['title']} - {failed['error']}")
                    )
        else:
            self.stdout.write(self.style.ERROR(f"❌ Error: {result['error']}"))


# Simple API views (optional) - views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json



@csrf_exempt
@require_http_methods(["POST"])
def api_send_post(request):
    """API endpoint to send immediate post"""
    try:
        data = json.loads(request.body)
        result = send_immediate_post(
            title=data.get('title', ''),
            content=data.get('content', ''),
            image_path=data.get('image_path'),
            image_url=data.get('image_url')
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_schedule_post(request):
    """API endpoint to schedule a post"""
    try:
        data = json.loads(request.body)
        post = create_telegram_post(
            title=data.get('title', ''),
            content=data.get('content', ''),
            image_path=data.get('image_path'),
            image_url=data.get('image_url'),
            scheduled_time=data.get('scheduled_time')
        )
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'message': 'Post scheduled successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def api_send_scheduled(request):
    """API endpoint to send scheduled posts"""
    try:
        force_all = request.GET.get('force', 'false').lower() == 'true'
        result = send_scheduled_posts(force_all=force_all)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# .env file template
"""
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username_or_channel_id
"""