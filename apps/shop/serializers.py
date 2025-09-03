from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from .models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new user accounts.

    Handles user registration with email authentication according to test assignment requirements.
    Only requires email, password, and username fields.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_password(self, value: str) -> str:
        """
        Validate password using Django's built-in validators and hash it.

        Args:
            value (str): Raw password string.

        Returns:
            str: Hashed password.

        Raises:
            serializers.ValidationError: If password doesn't meet requirements.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return make_password(value)

    def validate_email(self, value: str) -> str:
        """
        Validate that email is unique.

        Args:
            value (str): Email address.

        Returns:
            str: Validated email address.

        Raises:
            serializers.ValidationError: If email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.

    Validates credentials and returns user instance if authentication is successful.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, attrs):
        """
        Validate user credentials.

        Args:
            attrs (dict): Dictionary containing email and password.

        Returns:
            dict: Validated attributes with user instance.

        Raises:
            serializers.ValidationError: If credentials are invalid.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid email or password.')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password.')
