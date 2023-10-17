import datetime

from django.contrib.auth import get_user_model
from django.core import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from Digithup import settings

User = get_user_model()


class UpdateLastActivityMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated():
            User.objects.filter(user__id=request.user.id) \
                           .update(last_activity=timezone.now())