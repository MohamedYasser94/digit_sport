# from django.urls import path, re_path
#
# from core.consumers.consumers import NotificationConsumer, ChatConsumer
#
# websocket_urlpatterns = [
#     path('ws/dashboard/messenger/<str:room_name>/', ChatConsumer.as_asgi()),
#     # path('ws/dashboard/notifications/', NotificationConsumer.as_asgi()),
#
#
#     re_path(r"ws/dashboard/notifications/$", NotificationConsumer.as_asgi()),
#
# ]