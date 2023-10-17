
from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.core.serializers.python import Serializer
from core.constants import MSG_TYPE_MESSAGE
from core.models.chat import PrivateChatRoom, Room


def find_or_create_private_chat(user1, user2):
	try:
		chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
	except PrivateChatRoom.DoesNotExist:
		try:
			chat = PrivateChatRoom.objects.get(user1=user2, user2=user1)
		except PrivateChatRoom.DoesNotExist:
			chat = PrivateChatRoom(user1=user1, user2=user2)
			chat.save()
	return chat

def find_or_create_room(recipient_one, recipient_two):
	try:
		room_object = Room.objects.get(recipient_one=recipient_one, recipient_two=recipient_two)
	except Exception as e:
		print('Error finding room', e)
		try:
			room_object = Room.objects.get(recipient_one=recipient_two, recipient_two=recipient_one)
		except Exception as e:
			print('Error finding room2', e)
			room_object = Room(recipient_one=recipient_one, recipient_two=recipient_two,created_by=recipient_one)
			room_object.save()
	return room_object

def calculate_timestamp(timestamp):
	"""
	1. Today or yesterday:
		- EX: 'today at 10:56 AM'
		- EX: 'yesterday at 5:19 PM'
	2. other:
		- EX: 05/06/2020
		- EX: 12/28/2020
	"""
	ts = ""
	# Today or yesterday
	if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
		str_time = datetime.strftime(timestamp, "%I:%M %p")
		str_time = str_time.strip("0")
		ts = f"{naturalday(timestamp)} at {str_time}"
	# other days
	else:
		str_time = datetime.strftime(timestamp, "%m/%d/%Y")
		ts = f"{str_time}"
	return str(ts)



class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'msg_type': MSG_TYPE_MESSAGE})
        dump_object.update({'msg_id': str(obj.id)})
        dump_object.update({'user_id': str(obj.user.id)})
        dump_object.update({'email': str(obj.user.email)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'image': str(obj.user.image.url)})
        dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
        return dump_object



class LazyAccountEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'id': str(obj.id)})
        dump_object.update({'email': str(obj.email)})
        dump_object.update({'image': str(obj.image.url)})
        return dump_object


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

		# dump_object['notification_type'] = obj.get_content_object_type()
		dump_object['notification_id'] = str(obj.pk)
		dump_object['verb'] = obj.verb

		dump_object['is_read'] = str(obj.read)
		dump_object['natural_timestamp'] = str(naturaltime(obj.timestamp))
		dump_object['timestamp'] = str(obj.timestamp)
		dump_object |= {'actions': {'redirect_url': str(obj.redirect_url),}, "from": {"image_url": str(obj.from_user.image.url)}}




		return dump_object






