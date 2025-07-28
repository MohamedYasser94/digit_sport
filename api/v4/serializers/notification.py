from django.contrib.auth import get_user_model
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.serializers.python import Serializer
from django.utils.timezone import now
from rest_framework import serializers

from core.models.notifications import *

User = get_user_model()


############ Enmail  Notifcation ##################



class AdminNotificationSerializer(serializers.ModelSerializer):

	timesince = serializers.SerializerMethodField()
	class Meta:
		model = Notification
		fields = "__all__"

	def get_timesince(self, obj):
		current_datetime = now()
		time_difference = current_datetime - obj.created_at
		timesince = time_difference.total_seconds()
		if timesince < 60:
			return str(int(timesince)) + " seconds ago"
		elif timesince < 60 * 60:
			return str(int(timesince / 60)) + " minutes ago"
		elif timesince < 60 * 60 * 24:
			return str(int(timesince / (60 * 60))) + " hours ago"
		elif timesince < 60 * 60 * 24 * 7:
			return str(int(timesince / (60 * 60 * 24))) + " days ago"
		else:
			return obj.created_at.strftime("%B %d, %Y")




class LazyNotificationEncoder(Serializer):
    """
    Serialize a Notification into JSON.
    There are 3 types
        1. FriendRequest
        2. FriendList
        3. UnreadChatRoomMessage
    """

    def get_dump_object(self, obj):
        dump_object = {}
        if obj.get_content_object_type() == "FriendRequest":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'is_active': str(obj.content_object.is_active)})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "image_url": str(obj.from_user.profile_image.url)
                }
            })
        if obj.get_content_object_type() == "FriendList":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'is_read': str(obj.read)})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "image_url": str(obj.from_user.profile_image.url)
                }
            })
        if obj.get_content_object_type() == "UnreadChatRoomMessages":
            dump_object.update({'notification_type': obj.get_content_object_type()})
            dump_object.update({'notification_id': str(obj.pk)})
            dump_object.update({'verb': obj.verb})
            dump_object.update({'natural_timestamp': str(naturaltime(obj.timestamp))})
            dump_object.update({'timestamp': str(obj.timestamp)})
            dump_object.update({
                'actions': {
                    'redirect_url': str(obj.redirect_url),
                },
                "from": {
                    "title": str(obj.content_object.get_other_user.username),
                    "image_url": str(obj.content_object.get_other_user.profile_image.url)
                }
            })

        return dump_object


class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceInfo
        fields = "__all__"