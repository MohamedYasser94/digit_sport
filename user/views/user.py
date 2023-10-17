from datetime import datetime, timedelta

import pytz
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth import (
    login as auth_login,
)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import resolve_url
from django.template.loader import render_to_string, get_template
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, urlencode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView

from core.forms.users import  PasswordResetForm, SetPasswordForm
from core.models.core import SystemSetting
from core.models.subscriptions import Subscription, Membership, Coupon
from helper.commonHelper import FRONTEND_TEMPLATES, FRONTEND_TEMPLATES, BACKEND_TEMPLATES
from helper.decorators import unauthenticated_user
from user.forms.forms import UserSignUpForm, ResendActivationEmailForm, UserLoginForm
from user.models import UserGeoInfo
from user.signals import user_logged_in

User = get_user_model()
UserModel = get_user_model()


@unauthenticated_user
def CustomerRegister(request):
    system_setting = SystemSetting.objects.get(title='Digithup')
    if request.method == 'GET':
        context = {'form': UserSignUpForm(),
                   'system_setting': system_setting, }
        return render(request, f'{BACKEND_TEMPLATES}/login/CustomerRegister.html', context)

    if request.method == 'POST':
        system_registration = SystemSetting.objects.get(title='Digithup').registration

        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if system_registration == 'NotNeedActive':
                print('not need active')
                user.is_active = 'Inactive'
                user.is_staff = 'Inactive'
                user.save()
                context = {
                    'email': user.email,
                    'system_setting': system_setting,
                }
                return resolve_url('user:CustomerLogin')

            else:
                user.is_active = 'Inactive'
                user.is_staff = 'Inactive'
                user.is_customer = 'Active'
                user.save()
                group = Group.objects.get(name='customer')
                group.user_set.add(user)
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string(f'{BACKEND_TEMPLATES}/login/UserActiveEmailMessage.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                print('email send')
                messages.success(request, _('Your account has been created successfully'), extra_tags='User SignUp')
                context = {
                    'email': user.email,
                    'system_setting': system_setting,
                }
                return render(request, f'{BACKEND_TEMPLATES}/login/UserActiveEmailSent.html', context)
        else:
            messages.error(request, _('Something Wrong Please Try Again'), extra_tags='User SignUp')
    else:
        form = UserSignUpForm()

    context = {
        'form': form,
        'system_setting': system_setting,
    }
    return render(request, f'{BACKEND_TEMPLATES}/login/CustomerRegister.html', context)


def user_membership(request, user):
    system_setting = SystemSetting.objects.get(title='Digithup')
    print('membership', 1)
    print('membership user', user)

    try:
        Group.objects.get_or_create(name='Membership')
        membership = Membership.objects.get(membership_type='Free')
        membership_user = User.objects.get(id=user)
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=membership.duration)
        status = 'Active'
        subscription_object = Subscription(sender_model=ContentType.objects.get(model='User'),
                                           sender_id=request.user.id,
                                           owner_model=ContentType.objects.get(model='User'), owner_id=user,
                                           membership=membership, start_date=start_date, end_date=end_date,
                                           expires=end_date, status=status)
        subscription_object.save()

        group = Group.objects.get(name='Membership')
        group.user_set.add(membership_user.id)
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        message = get_template(f'{FRONTEND_TEMPLATES}/login/UserActiveEmailMessage.html').render(
            {'user': membership_user, 'domain': current_site.domain,
             'uid': urlsafe_base64_encode(force_bytes(membership_user)),
             'token': default_token_generator.make_token(membership_user)})

        to_email = membership_user.email
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.content_subtype = 'html'
        if system_setting.registration == 'NeedActive':
            email.send()
    except Exception as e:

        print('membership ', e)
        user = User.objects.get(id=user)
        user.delete()
        if e:
            messages.error(request, _('Something Wrong Please Try Again'), extra_tags='Member ship')
            return render(request, f'{FRONTEND_TEMPLATES}/login/CustomerRegister.html')


@csrf_protect
@unauthenticated_user
def UserActivate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = 'Active'
        user.save()
        return render(request, f'{BACKEND_TEMPLATES}/login/UserActiveEmailDone.html')
    else:
        return render(request, f'{BACKEND_TEMPLATES}/login/UserActiveEmailInvalid.html')


# @unauthenticated_user
class UserLogin(View):
    """
    Description:Will be used to login and logout users.\n
    """
    template_name = f'{BACKEND_TEMPLATES}/login/CustomerLogin.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect('home:HomeIndex')
        else:
            form = UserLoginForm()
            context = {
                "title": "Login",
                "form": form
            }
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST or None)
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post or None
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(
                        0)  # <-- Here if the remember me is False, that is why expiry is set to 0 seconds. So it will automatically close the session after the browser is closed.

            if user is not None:
                login(request, user)
                user_logged_in.send(
                    user.__class__,
                    instance=user,
                    request=request
                )
                if not user.is_superuser:
                    pass
                    # user_subscribe(request, user)
                try:
                    del request.session['guest_email_id']

                except:
                    return redirect("/")
                else:
                    return redirect("/")

            else:
                print("error")
                return redirect("/login/")

        context = {
            "title": "Login",
            "form": form
        }
        return render(request, self.template_name, context)


def UserLogout(request):
    logout(request)
    return redirect('home:HomeIndex')


def user_subscribe(request, user):
    if user.is_authenticated:
        if subscription := Subscription.objects.get(user_membership__user=request.user.id):
            expires = subscription.expires_in
            utc = pytz.UTC
            print('expires', expires)
            if expires < datetime.now(utc):
                subscription.active = False
                subscription.save()
                user.subscribe = False
                user.save()


def resend_activation_email(request):
    email_body_template = f'{BACKEND_TEMPLATES}/login/UserReactiveEmailMessage.html'
    email_subject_template = f'{BACKEND_TEMPLATES}/login/activation_email_subject.txt'

    if not request.user.is_anonymous:
        return HttpResponseRedirect('/')

    context = {}

    form = None
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email, is_active=False)

            if not users.count():
                form._errors["Email"] = _("Account for email address is not registered or already activated.")

            REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')
            mail_subject = 'Activate your account.'
            for user in users:
                activation_key = signing.dumps(
                    obj=getattr(user, user.USERNAME_FIELD),
                    salt=REGISTRATION_SALT,
                )
                context = {'activation_key': activation_key, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                           'site': get_current_site(request)}

                current_site = get_current_site(request)
                message = render_to_string(f'{BACKEND_TEMPLATES}/login/UserActiveEmailMessage.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                return render(request, f'{BACKEND_TEMPLATES}/login/UserActiveEmailSent.html', context)

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form": form})
    return render(request, f'{BACKEND_TEMPLATES}/login/CustomerResendEmail.html', context)


###########Rest Password#############


class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'good/login/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = 'good/login/password_reset_email.html'
    subject_template_name = 'good/login/password_reset_subject.txt'
    success_url = reverse_lazy('user:FrontPasswordResetDone')
    template_name = f'{BACKEND_TEMPLATES}/login/UserPasswordResetForm.html'
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect, )
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {

            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = f'{BACKEND_TEMPLATES}/login/UserPasswordResetDone.html'
    title = _('Password reset sent')


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('user:FrontPasswordResetComplete')
    template_name = f'{BACKEND_TEMPLATES}/login/UserPasswordChange.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Vendor the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = f'{BACKEND_TEMPLATES}/login/UserPasswordResetComplete.html'
    title = _('Password reset complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordForm(request.user)
    return render(request, f'{BACKEND_TEMPLATES}/login/UserPasswordChange.html', {'form': form})


def facebook_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('user:CustomerFaceBookLogin')
    )
    if ('code' in request.GET):
        code = request.GET.get('code')
        url = 'https://graph.facebook.com/v2.10/oauth/access_token'
        params = {
            'client_id': settings.FB_APP_ID,
            'client_secret': settings.FB_APP_SECRET,
            'code': code,
            'redirect_uri': redirect_uri,
        }
        response = requests.get(url, params=params)
        params = response.json()
        params.update({
            'fields': 'id,last_name,first_name,picture,birthday,email,gender'
        })
        url = 'https://graph.facebook.com/me'
        user_data = requests.get(url, params=params).json()
        email = user_data.get('email')
        if email:
            user, _ = User.objects.get_or_create(email=email, username=email)
            gender = user_data.get('gender', '').lower()
            dob = user_data.get('birthday')
            if gender == 'male':
                gender = 'M'
            elif gender == 'female':
                gender = 'F'
            else:
                gender = 'O'
            data = {
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'fb_avatar': user_data.get('picture', {}).get('data', {}).get('url'),
                'gender': gender,
                'dob': datetime.strptime(dob, "%m/%d/%Y") if dob else None,
                'is_active': True
            }
            user.__dict__.update(data)
            user.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
        else:
            messages.error(
                request,
                'Unable to login with Facebook Please try again'
            )
        return redirect('/')
    else:
        url = "https://graph.facebook.com/oauth/authorize"
        params = {
            'client_id': settings.FB_APP_ID,
            'redirect_uri': redirect_uri,
            'scope': 'email,public_profile,user_birthday'
        }
        url += '?' + urlencode(params)
        return redirect(url)


def google_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('user:CustomerGoogleLogin')
    )
    if ('code' in request.GET):
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': settings.GP_CLIENT_ID,
            'client_secret': settings.GP_CLIENT_SECRET
        }
        url = 'https://accounts.google.com/o/oauth2/token'
        response = requests.post(url, data=params)
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        access_token = response.json().get('access_token')
        response = requests.get(url, params={'access_token': access_token})
        user_data = response.json()
        email = user_data.get('email')
        if email:
            user, _ = User.objects.get_or_create(email=email, username=email)
            gender = user_data.get('gender', '').lower()
            if gender == 'male':
                gender = 'M'
            elif gender == 'female':
                gender = 'F'
            else:
                gender = 'O'
            data = {
                'first_name': user_data.get('title', '').split()[0],
                'last_name': user_data.get('family_name'),
                'google_avatar': user_data.get('picture'),
                'gender': gender,
                'is_active': True
            }
            user.__dict__.update(data)
            user.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
        else:
            messages.error(
                request,
                'Unable to login with Gmail Please try again'
            )
        return redirect('/')
    else:
        url = "https://accounts.google.com/o/oauth2/auth?client_id=%s&response_type=code&scope=%s&redirect_uri=%s&state=google"
        scope = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ]
        scope = " ".join(scope)
        url = url % (settings.GP_CLIENT_ID, scope, redirect_uri)
        return redirect(url)


def UserGeoInfoUpdate(request, user):
    try:
        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        device_type = ""
        browser_type = ""
        browser_version = ""
        os_type = ""
        os_version = ""
        if request.user_agent.is_mobile:
            device_type = "Mobile"
        if request.user_agent.is_tablet:
            device_type = "Tablet"
        if request.user_agent.is_pc:
            device_type = "PC"
        browser_type = request.user_agent.browser.family
        browser_version = request.user_agent.browser.version_string
        os_type = request.user_agent.os.family
        os_version = request.user_agent.os.version_string
        g = None
        location = g.city(ip)
        location_country = location["country_name"]
        location_city = location["city"]
        try:
            geo_info = UserGeoInfo.objects.get(user=user)
            geo_info.user = user
            geo_info.ip = ip
            geo_info.device_type = device_type
            geo_info.browser_type = browser_type
            geo_info.os_type = os_type
            geo_info.os_version = os_version
            geo_info.location_country = location_country
            geo_info.location_city = location_city
            geo_info.save()
        except Exception as e:

            geo_info = UserGeoInfo(user=user, ip=ip, device_type=device_type, browser_version=browser_version,
                                   browser_type=browser_type,
                                   os_type=os_type, os_version=os_version, location_country=location_country,
                                   location_city=location_city)
            geo_info.save()
    except Exception as e:
        pass


def TestPages(request):
    return render(request, f'{BACKEND_TEMPLATES}/login/UserReactiveEmailMessage.html', )
