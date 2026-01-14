import os
import json

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v4.renderers import *
from api.v4.serializers.user import *
from api.v4.utils import Util

User = get_user_model()


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']





@csrf_exempt
def UserRegister(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phone = data.get('phone', None)

            if not all([email, password, first_name, last_name]):
                return JsonResponse({
                    'error': True,
                    'message': 'All fields are required.'
                }, status=status.HTTP_200_OK)

            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'error': True,
                    'message': 'This email already exists.'
                }, status=status.HTTP_200_OK)

            try:
                user = User(email=email)
                user.set_password(password) # Use set_password for proper hashing
                user.first_name = first_name
                user.last_name = last_name
                user.phone = phone
                user.is_active = 'Active'  # Set to Active by default
                user.access_level = 'Customer'
                user.save()

                # Generate and return a token for the new user
                token, created = Token.objects.get_or_create(user=user)

                # Serialize user details
                user_data = UserSerializer(user).data

                # Return user data along with the token
                response_data = {
                    'error': False,
                    'message': 'User created successfully',
                    'data': user_data,
                    'token': str(token),
                }

                return JsonResponse(response_data, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return JsonResponse({
                    'error': True,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return JsonResponse({
                    'error': True,
                    'message': f'Error creating user: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return JsonResponse({
                'error': True,
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JsonResponse({
        'error': True,
        'message': 'Method not allowed'
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])  # Add this to bypass authentication for login
def UserLogin(request):
    """
    Handles user login using email and password.
    On success, it returns JWT access and refresh tokens and saves the FCM token.
    """
    email = request.data.get('email')
    password = request.data.get('password')



    if not email or not password:
        return Response({
            'status': False,
            'message': 'Email and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(email=email, password=password)

    if user is not None:
        # ▼▼▼ START OF CORRECTED LOGIC ▼▼▼
        # 1. Get the optional fcm_token from the request.
        fcm_token = request.data.get('fcm_token')

        # 2. If an fcm_token was sent by the client, always update it.
        # This ensures the user's latest device gets notifications.
        if fcm_token:
            user.fcm_token = fcm_token
            # Use update_fields for an efficient database query.
            user.save(update_fields=['fcm_token'])
        # ▲▲▲ END OF CORRECTED LOGIC ▲▲▲

        refresh = RefreshToken.for_user(user)


        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'access_level': user.access_level,
            'slug': user.slug,
            'profile': user.image.url if user.image else None,
            'mobile': user.phone,

        }

        response_data = {
            'status': True,
            'message': 'User logged in successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        # This is the block that returns 401 for bad credentials
        return Response({
            'status': False,
            'message': 'Invalid credentials, try again'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def UserLogout(request):
    """
    Logs out a user by blacklisting their refresh token.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         absurl + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'UserToken is not valid, please request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)



@csrf_exempt
def ApiCheckUserDataExist(request, data):
    if request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    user = False
    user_exist = False
    if request.method == 'POST':
        type = request.POST.get('type')

        if type == 'email':
            user = User.objects.filter(email=data).count()
        elif type == 'phone':
            user = User.objects.filter(phone=data).count()
        if user > 0:
            user_exist = True
            return JsonResponse(user_exist, safe=False)
        elif user <= 0:
            user_exist = False
            return JsonResponse(user_exist, safe=False)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def ContactUs(request):
    """
    Handles contact us / support requests from the mobile app.
    Accepts: name, email, phone, subject, message
    """
    try:
        name = request.data.get('name', '')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        subject = request.data.get('subject', '')
        message = request.data.get('message', '')

        # Validate required fields
        if not all([name, email, message]):
            return Response({
                'error': True,
                'message': 'Name, email, and message are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Here you can add logic to:
        # 1. Save to database (create a ContactMessage model)
        # 2. Send email notification to admin
        # 3. Send confirmation email to user

        # For now, just log and return success
        print(f'Contact Us Request - Name: {name}, Email: {email}, Subject: {subject}')
        print(f'Message: {message}')

        # Optional: Send email to admin
        try:
            from api.v4.utils import Util
            email_data = {
                'email_subject': f'Contact Us: {subject}' if subject else 'Contact Us Request',
                'email_body': f'''
New contact request received:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject if subject else 'No subject'}

Message:
{message}
                ''',
                'to_email': settings.RECIPIENT_ADDRESS if hasattr(settings, 'RECIPIENT_ADDRESS') else 'support@example.com'
            }
            Util.send_email(email_data)
        except Exception as email_error:
            # Don't fail the request if email fails
            print(f'Email notification failed: {str(email_error)}')

        return Response({
            'error': False,
            'message': 'Thank you for contacting us. We will get back to you soon.',
            'status': 'success'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f'Contact Us Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return Response({
            'error': True,
            'message': f'An error occurred while processing your request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
