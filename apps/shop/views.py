from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product
from .serializers import CreateUserSerializer, LoginSerializer


class AuthViewSet(ViewSet):
    """
    ViewSet for user authentication operations.

    Provides endpoints for user registration and login with JWT token generation.
    """

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """
        Register a new user account.

        Args:
            request: HTTP request containing user data

        Returns:
            Response: Success message with 201 status or errors with 400 status
        """
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    'message': 'User created successfully',
                    'user_id': user.id,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({
                    'error': 'User with this email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate user and return JWT tokens.

        Args:
            request: HTTP request containing email and password

        Returns:
            Response: JWT tokens with 200 status or errors with 400 status
        """
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': 'Login successful',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
