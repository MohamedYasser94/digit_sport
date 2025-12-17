from django.contrib import auth
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


from user.models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    class Meta(object):
        model = User
        fields = ['id',  'first_name','last_name','phone','email','image','access_level','is_active','is_verified','token']
    def get_token(self, obj):
        user = User.objects.get(email=obj.email)

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'email': 'The email should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone']

    def validate(self, attrs):
        if email := attrs.get('email', ''):
            return attrs
        else:
            raise serializers.ValidationError(self.default_error_messages)

    def create(self, validated_data):
        user_object = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],

        )
        user_object.set_password(validated_data['password'])
        user_object.save()
        return user_object


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']

class LoginSerializer(serializers.Serializer):





    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    email = serializers.CharField(
        label="Email",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        # Take username and password from request
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong email or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "email" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs
class CustomerLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        # return {
        #     'email': user.email,
        #     'tokens': user.tokens
        # }

        return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('UserToken is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')



class CheckUserExistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email','phone')






# class UserAddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserAddress
#         fields = '__all__'
# class VerificationFieldValuesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VerificationFieldValues
#         fields = '__all__'

# class VerificationRequestSerializer(serializers.ModelSerializer):
#     verification_field_values = VerificationFieldValuesSerializer(many=True, read_only=True)

#     class Meta:
#         model = VerificationRequestModel
#         fields = [
#             'id',
#             'user_id',
#             'status',
#             'created_at',
#             'updated_at',
#             'rejection_reason',
#             'verification_field_values'
#         ]