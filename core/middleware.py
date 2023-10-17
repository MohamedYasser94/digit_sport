from datetime import datetime

from django.contrib.auth import get_user_model

from core.models.subscriptions import Subscription

User = get_user_model()


class UserSubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated():
            print("custom middleware before next middleware/view")
            # Code to be executed for each request before
            # the view (and later middleware) are called.
            user = User.objects.get(id=request.user.id)
            subscription = Subscription.objects.filter(user_membership__user=request.user)
            if subscription.exists():
                expires = subscription.expires_in
                if expires < datetime.now():
                    subscription.active = False
                    subscription.save()
                    user.subscribe = False
                    user.save()
                request.user.subscription = subscription.last()
                print("subscription exists", request.user.subscription)

            response = self.get_response(request)

            # Code to be executed for each response after the view is called
            print("custom middleware after response or previous middleware")

            return response


from django.middleware.common import CommonMiddleware

# class DisableBackButtonMiddleware(CommonMiddleware):
#     def process_response(self, request, response):
#       # Do something
#       return response
