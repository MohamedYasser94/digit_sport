from typing import Optional, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from slugify import slugify

from core.models.notifications import ChatNotification


from digit_sport import settings
import uuid
User = get_user_model()


class Room(models.Model):
    private_room = models.BooleanField(default=False)
    passcode = models.CharField(max_length=128, blank=True, null=True, default=None)
    code = models.CharField(unique=False, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_by = models.ForeignKey(User, related_name='created_rooms', on_delete=models.CASCADE)
    recipient_one = models.ForeignKey(User, on_delete=models.CASCADE,related_name='room_recipient_one',blank=True, null=True)
    recipient_two= models.ForeignKey(User, on_delete=models.CASCADE,related_name='room_recipient_two',blank=True, null=True)
    # Users who are currently connected to the socket (Used to keep track of unread messages)
    connected_users = models.ManyToManyField(User, blank=True, related_name="room_connected_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse("core:room", kwargs={"pk": self.pk})

    def check_passcode(self, passcode):
        return check_password(passcode, self.passcode)


    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Room-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        if self.private_room:
            self.passcode = make_password(self.passcode)
        super(Room, self).save(*args, **kwargs)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

    class Meta:
        ordering = ('date_added',)

class PrivateChatRoom(models.Model):
    """
	A private room for people to chat in.
	"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")

    # Users who are currently connected to the socket (Used to keep track of unread messages)
    connected_users = models.ManyToManyField(User, blank=True, related_name="connected_users")

    is_active = models.BooleanField(default=False)

    def connect_user(self, user):
        """
		return true if user is added to the connected_users list
		"""
        is_user_added = False
        if user not in self.connected_users.all():
            self.connected_users.add(user)
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        """
		return true if user is removed from connected_users list
		"""
        is_user_removed = False
        if user in self.connected_users.all():
            self.connected_users.remove(user)
            is_user_removed = True
        return is_user_removed

    @property
    def group_name(self):
        """
		Returns the Channels Group title that sockets should subscribe to to get sent
		messages as they are generated.
		"""
        return f"PrivateChatRoom-{self.id}"


class RoomChatMessageManager(models.Manager):
    def by_room(self, room):
        return RoomChatMessage.objects.filter(room=room).order_by("-timestamp")


class RoomChatMessage(models.Model):
    """
	Chat message created by a user inside a Room
	"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False, )

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.content


class UnreadChatRoomMessages(models.Model):
    """
	Keep track of the number of unread messages by a specific user in a specific private chat.
	When the user connects the chat room, the messages will be considered "read" and 'count' will be set to 0.
	"""
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE, related_name="room")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    count = models.IntegerField(default=0)

    most_recent_message = models.CharField(max_length=500, blank=True, null=True)

    # last time msgs were read by the user
    reset_timestamp = models.DateTimeField()

    notifications = GenericRelation(ChatNotification)

    def __str__(self):
        return f"Messages that {str(self.user)} has not read yet."

    def save(self, *args, **kwargs):
        if not self.id:  # if just created, add a timestamp. Otherwise do not automatically change it ever.
            self.reset_timestamp = timezone.now()
        return super(UnreadChatRoomMessages, self).save(*args, **kwargs)

    @property
    def get_cname(self):
        """
		For determining what kind of object is associated with a Notification
		"""
        return "UnreadChatRoomMessages"

    @property
    def get_other_user(self):
        """
		Get the other user in the chat room
		"""
        if self.user == self.room.user1:
            return self.room.user2
        else:
            return self.room.user1


@receiver(post_save, sender=PrivateChatRoom)
def create_unread_chatroom_messages_obj(sender, instance, created, **kwargs):
    if created:
        unread_msgs1 = UnreadChatRoomMessages(room=instance, user=instance.user1)
        unread_msgs1.save()

        unread_msgs2 = UnreadChatRoomMessages(room=instance, user=instance.user2)
        unread_msgs2.save()


@receiver(pre_save, sender=UnreadChatRoomMessages)
def increment_unread_msg_count(sender, instance, **kwargs):
    """
	When the unread message count increases, update the notification.
	If one does not exist, create one. (This should never happen)
	"""
    if instance.id is None:  # new object will be created
        pass  # create_unread_chatroom_messages_obj will handle this scenario
    else:
        previous = UnreadChatRoomMessages.objects.get(id=instance.id)
        if previous.count < instance.count:  # if count is incremented
            content_type = ContentType.objects.get_for_model(instance)
            if instance.user == instance.room.user1:
                other_user = instance.room.user2
            else:
                other_user = instance.room.user1
            try:
                notification = ChatNotification.objects.get(target=instance.user, content_type=content_type,
                                                        object_id=instance.id)
                notification.verb = instance.most_recent_message
                notification.timestamp = timezone.now()
                notification.save()
            except ChatNotification.DoesNotExist:
                instance.notifications.create(
                    target=instance.user,
                    from_user=other_user,
                    redirect_url=f"{settings.BASE_URL}/api/v1/chat/?room_id={instance.room.id}",
                    # we want to go to the chatroom
                    verb=instance.most_recent_message,
                    content_type=content_type,
                )


@receiver(pre_save, sender=UnreadChatRoomMessages)
def remove_unread_msg_count_notification(sender, instance, **kwargs):
    """
	If the unread messge count decreases, it means the user joined the chat. So delete the notification.
	"""
    if instance.id is None:  # new object will be created
        pass  # create_unread_chatroom_messages_obj will handle this scenario
    else:
        previous = UnreadChatRoomMessages.objects.get(id=instance.id)
        if previous.count > instance.count:  # if count is decremented
            content_type = ContentType.objects.get_for_model(instance)
            try:
                notification = ChatNotification.objects.get(target=instance.user, content_type=content_type,
                                                        object_id=instance.id)
                notification.delete()
            except ChatNotification.DoesNotExist:
                pass
            # Do nothing


class PublicChatRoom(models.Model):
    # Room title
    title = models.CharField(max_length=255, unique=True, blank=False, )

    # all users who are authenticated and viewing the chat
    users = models.ManyToManyField(User, help_text="users who are connected to chat room.",
                                   )

    def __str__(self):
        return self.title

    def connect_user(self, user):
        """
		return true if user is added to the users list
		"""
        is_user_added = False
        if not user in self.users.all():
            self.users.add(user)
            self.save()
            is_user_added = True
        elif user in self.users.all():
            is_user_added = True
        return is_user_added

    def disconnect_user(self, user):
        """
		return true if user is removed from the users list
		"""
        is_user_removed = False
        if user in self.users.all():
            self.users.remove(user)
            self.save()
            is_user_removed = True
        return is_user_removed

    @property
    def group_name(self):
        """
		Returns the Channels Group title that sockets should subscribe to to get sent
		messages as they are generated.
		"""
        return "PublicChatRoom-%s" % self.id


class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        return PublicRoomChatMessage.objects.filter(room=room).order_by("-timestamp")


class PublicRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a PublicChatRoom
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(unique=False, blank=False, )

    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content
