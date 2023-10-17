from django.contrib.auth import get_user_model

from django.dispatch import Signal

User = get_user_model()
UserModel = get_user_model()
user_logged_in = Signal()
