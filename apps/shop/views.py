from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CreateUserSerializer, LoginSerializer


class RegisterAPIView(APIView):
    """
    API view for user registration.

    Handles POST requests to create new user accounts with email authentication.
    """
    serializer_class = CreateUserSerializer

    def post(self, request):
        """
        Create a new user account.

        Args:
            request: HTTP request containing user data

        Returns:
            Response: Success message with 201 status or errors with 400 status
        """
        serializer = self.serializer_class(data=request.data)

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


class LoginAPIView(APIView):
    """
    API view for user authentication and JWT token generation.

    Handles POST requests to authenticate users and return JWT tokens.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """
        Authenticate user and return JWT tokens.

        Args:
            request: HTTP request containing email and password

        Returns:
            Response: JWT tokens with 200 status or errors with 400 status
        """
        serializer = self.serializer_class(data=request.data)

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
