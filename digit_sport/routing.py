from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					# path('', NotificationConsumer.as_asgi()),
					# path('dashboard/messenger/chat/<room_id>/', ChatConsumer.as_asgi()),
					# path('public_chat/<room_id>/', PublicChatConsumer.as_asgi()),
			])
		)
	),
})
