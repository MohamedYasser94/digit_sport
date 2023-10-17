import json
from datetime import datetime

from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from core.models.chat import Room, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print('receive', text_data)
        data = json.loads(text_data)
        print('data', data)
        message = data['message']
        email = data['email']
        room = data['room']

        await self.save_message(email, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'email': email,
                'room': room
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        email = event['email']
        room = event['room']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'email': email,
            'room': room
        }))

    @sync_to_async
    def save_message(self, email, room, message):
        print('save_message', email, room, message)
        user = User.objects.get(email=email)
        room = Room.objects.get(slug=room)
        try:
            message_object = Message(user=user, room=room, content=message)
            message_object.save()
            print(' saving message')
        except Exception as e:
            print('Error saving message', e)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Perform any necessary connection setup here
        await self.accept()
        print('NotificationConsumerTest connect')
        await self.channel_layer.group_add(
            f'user_{self.scope["user"].id}',
            self.channel_name
        )

    async def disconnect(self, close_code):
        # Perform any necessary cleanup here
        pass

    async def receive(self, text_data):
        # Handle incoming data from WebSocket
        text_data_json = json.loads(text_data)
        # Process the received data here
        # You can use self.send() to send a response back to the people
        await self.send(text_data=json.dumps({
            'message': text_data_json['message'],
            'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        }))

    async def send_notification(self, event):
        message = event['message']
        print('async send_notification', message)
        await self.send(text_data=json.dumps({
            'message': message,
            'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }))

def send_notification(user_id, message):
    print('send_notification', user_id, message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'send_notification',
            'message': message,
        }
    )