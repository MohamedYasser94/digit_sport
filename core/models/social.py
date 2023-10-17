from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from core.models.notifications import ChatNotification
from core.utils.chat import find_or_create_private_chat
from digit_sport import settings
from helper.modelHelper import Active_Status, Friend_Request_Status, Follower_Type

User = get_user_model()


class FriendList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    # set up the reverse relation to GenericForeignKey
    notifications = GenericRelation(ChatNotification)

    def __str__(self):
        return self.user.email

    def add_friend(self, account):
        print('model account',account)
        """
		Add a new friend.
		"""
        if account not in self.friends.all():
            self.friends.add(account)
            self.save()

            content_type = ContentType.objects.get_for_model(self)

            # Create notification
            # Can create this way if you want. Doesn't matter.
            # Notification(
            # 	target=self.user,
            # 	from_user=account,
            # 	redirect_url=f"{settings.BASE_URL}/account/{account.pk}/",
            # 	verb=f"You are now friends with {account.username}.",
            # 	content_type=content_type,
            # 	object_id=self.id,
            # ).save()

            self.notifications.create(
                target=self.user,
                from_user=account,
                redirect_url=f"{settings.BASE_URL}/profile/{account.slug}/",
                verb=f"You are now friends with {account.email}.",
                content_type=content_type,
            )
            self.save()

            # Create a private chat (or activate an old one)
            chat = find_or_create_private_chat(self.user, account)
            if not chat.is_active:
                chat.is_active = True
                chat.save()

    def remove_friend(self, account):
        """
		Remove a friend.
		"""
        if account in self.friends.all():
            self.friends.remove(account)

            # Deactivate the private chat between these two users
            chat = find_or_create_private_chat(self.user, account)
            if chat.is_active:
                chat.is_active = False
                chat.save()

    def unfriend(self, removee):
        """
		Initiate the action of unfriending someone.
		"""
        remover_friends_list = self  # person terminating the friendship

        # Remove friend from remover friend list
        remover_friends_list.remove_friend(removee)

        # Remove friend from removee friend list
        friends_list = FriendList.objects.get(user=removee)
        friends_list.remove_friend(remover_friends_list.user)

        content_type = ContentType.objects.get_for_model(self)

        # Create notification for removee
        friends_list.notifications.create(
            target=removee,
            from_user=self.user,
            redirect_url=f"{settings.BASE_URL}/account/{self.user.pk}/",
            verb=f"You are no longer friends with {self.user.email}.",
            content_type=content_type,
        )

        # Create notification for remover
        self.notifications.create(
            target=self.user,
            from_user=removee,
            redirect_url=f"{settings.BASE_URL}/account/{removee.pk}/",
            verb=f"You are no longer friends with {removee.email}.",
            content_type=content_type,
        )

    @property
    def get_cname(self):
        """
		For determining what kind of object is associated with a Notification
		"""
        return "FriendList"

    def is_mutual_friend(self, friend):
        """
		Is this a friend?
		"""
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    """
	A friend request consists of two main parts:
		1. SENDER
			- Person sending/initiating the friend request
		2. RECIVER
			- Person receiving the friend friend
	"""

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=False, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Friend_Request_Status, default='NOREQUEST')
    notifications = GenericRelation(ChatNotification)

    def __str__(self):
        return f'Name of employee: {self.sender}'

    def accept(self):
        """
		Accept a friend request.
		Update both SENDER and RECEIVER friend lists.
		"""


        if receiver_friend_list := FriendList.objects.get(user=self.receiver):
            content_type = ContentType.objects.get_for_model(self)

            # Update notification for RECEIVER

            receiver_notification = ChatNotification.objects.get(target=self.receiver,
                                                                           content_type=content_type,
                                                                           object_id=self.id)
            receiver_notification.is_active = False
            receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender}/"
            receiver_notification.verb = f"You accepted {self.sender}'s friend request."
            receiver_notification.timestamp = timezone.now()
            receiver_notification.save()
            receiver_friend_list.add_friend(self.sender)

            if sender_friend_list := FriendList.objects.get(user=self.sender):
                # Create notification for SENDER
                self.notifications.create(
                    target=self.sender,
                    from_user=self.receiver,
                    redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
                    verb=f"{self.receiver} accepted your friend request.",
                    content_type=content_type,
                )

                sender_friend_list.add_friend(self.receiver)
                # sender_friend_list.save()
                self.is_active = False
                self.status = 'APPROVED'
                self.save()
            return receiver_notification  # we will need this later to update the realtime notifications

    def decline(self):
        """
		Decline a friend request.
		Is it "declined" by setting the `is_active` field to False
		"""
        self.is_active = False
        self.status='DECLINE'
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        # Update notification for RECEIVER
        notification = ChatNotification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
        notification.is_active = False
        notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
        notification.verb = f"You declined {self.sender}'s friend request."
        notification.from_user = self.sender
        notification.timestamp = timezone.now()
        notification.save()

        # Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            verb=f"{self.receiver.email} declined your friend request.",
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            content_type=content_type,
        )

        return notification

    def cancel(self):
        """
		Cancel a friend request.
		Is it "cancelled" by setting the `is_active` field to False.
		This is only different with respect to "declining" through the notification that is generated.
		"""
        self.is_active = False
        self.status='NOREQUEST'
        self.save()

        content_type = ContentType.objects.get_for_model(self)

        # Create notification for SENDER
        self.notifications.create(
            target=self.sender,
            verb=f"You cancelled the friend request to {self.receiver.email}.",
            from_user=self.receiver,
            redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
            content_type=content_type,
        )

        notification = ChatNotification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
        notification.verb = f"{self.sender.email} cancelled the friend request sent to you."
        # notification.timestamp = timezone.now()
        notification.read = False
        notification.save()


    def get_cname(self):
        """
		For determining what kind of object is associated with a Notification
		"""
        return "FriendRequest"




class Following(models.Model):
    """
    A follower consists of two main parts:
        1. FOLLOWER
            - Person following another person
        2. FOLLOWING
            - Person being followed by another person
    """
    sender_model = models.ForeignKey(ContentType, related_name='following_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='following_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='following_owner', on_delete=models.PROTECT, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    type = models.CharField(max_length=20, choices=Follower_Type, default='FOLLOWER')

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    is_active = models.BooleanField(blank=False, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Friend_Request_Status, default='NOREQUEST')
    notifications = GenericRelation(ChatNotification)

    def __str__(self):
        return f'Name of employee: {self.follower}'

    def accept(self):
        """
        Accept a follower request.
        Update both FOLLOWER and FOLLOWING follower lists.
        """

        if following_follower_list := Following.objects.get(user=self.following):
            content_type = ContentType.objects.get_for_model(self)

            # Update notification for FOLLOWING

            following_notification = ChatNotification.objects.get(target=self.following,
                                                                           content_type=content_type,
                                                                           object_id=self.id)
            following_notification.is_active = False
            following_notification.redirect_url = f"{settings.BASE_URL}/account/{self.follower}/"
            following_notification.verb = f"You accepted {self.follower}'s follower request."
            following_notification.timestamp = timezone.now()
            following_notification.save()
            following_follower_list.add_follower(self.follower)

            if follower_follower_list := Following.objects.get(user=self.follower):
                # Create notification for FOLLOWER
                self.notifications.create(
                    target=self.follower,
                    from_user=self.following,
                    redirect_url=f"{settings.BASE_URL}/account/{self.following.pk}/",
                    verb=f"{self.following} accepted your follower request.",
                    content_type=content_type,
                )

                follower_follower_list.add_follower(self.following)
                # follower_follower_list.save()
                self.is_active = False
                self.status = 'APPROVED'
                self.save()
            return following_notification  # we will need this later to update the realtime notifications

    def decline(self):
        """
        Decline a follower request.
        Is it "declined" by setting the `is_active` field to False
        """
        self.is_active = False



