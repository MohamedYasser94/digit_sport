from unittest import TestCase

from django.contrib.auth import get_user_model
from django.core import mail
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from api.v1.utils import Util
from apps.wallet.models.models import WalletResetPassword, WalletLocked

User = get_user_model()






@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))

# @csrf_exempt
def ApiWalletRequestResetCode(request, user_id):
    if request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if User.objects.filter(id=user_id).exists():

        user = User.objects.get(id=user_id)
        wallet_locked = WalletLocked.objects.get(user=user)
        wallet_reset_code = WalletResetPassword.objects.get(wallet_locked=wallet_locked)
        reset_code = wallet_reset_code.reset_code
        email_body = 'Hello, \n Use link below to reset your password  \n' + \
                     reset_code
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Reset your Wallet Password'}
        Util.send_email(data)

    return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class EmailTest(TestCase):
    def test_send_email(self):
        print(3)
        mail.send_mail('Subject here', 'Here is the message.',
            'm.hitler.kgb89@gmail.com', ['iarbic90@gmail.com'],
            fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')