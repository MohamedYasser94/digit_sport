from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string

from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
import importlib
import smtplib

from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import threading

from django_user_agents.utils import text_type

from core.utils.exceptions import InternalServerError


def validate_email(value: str) -> tuple[bool, str]:
    """Validate a single email."""
    message_invalid = 'Enter a valid email address.'

    if not value:
        return False, message_invalid
    # Check the regex, using the validate_email from django.
    try:
        django_validate_email(value)
    except ValidationError:
        return False, message_invalid

    return True, ''
class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.active) + text_type(user.pk) + text_type(timestamp))


account_activation_token = AppTokenGenerator()



class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()



def import_elm_from_str(string):
    elements = string.split('.')
    module, elm = '.'.join(elements[:-1]), elements[-1]
    module = importlib.import_module(module)
    return getattr(module, elm)


def send_mail(subject, recipient_list, err_msg, template_name, context=None):
    context = context or {}
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        mail.send_mail(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            message=plain_message,
            html_message=html_message,
        )
    except smtplib.SMTPException as err:
        raise InternalServerError(err_msg) from err