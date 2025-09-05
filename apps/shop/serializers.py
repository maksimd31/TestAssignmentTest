from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from .models import User, Product

# Constants
MIN_PASSWORD_LENGTH = 8


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating new user accounts."""

    password = serializers.CharField(write_only=True, min_length=MIN_PASSWORD_LENGTH)

    class Meta:
        model = User
        fields = ('email', 'password', 'username')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_password(self, value: str) -> str:
        """Validate and hash password."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return make_password(value)

    def validate_email(self, value: str) -> str:
        """Ensure email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for user authentication."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=MIN_PASSWORD_LENGTH)

    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Must include email and password.')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product data."""

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'stock', 'category', 'image')
        read_only_fields = ('id',)
