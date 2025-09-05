from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product
from .paginations import ProductPagination
from .permissions import IsAdminOrReadOnly
from .serializers import CreateUserSerializer, LoginSerializer, ProductSerializer


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





class ProductViewSet(ViewSet):
    """
    ViewSet for managing products with full CRUD operations.

    Supports filtering by category and price range with pagination.
    Admin-only permissions for write operations.
    """

    permission_classes = [IsAdminOrReadOnly]
    pagination_class = ProductPagination

    def get_queryset(self, request):
        """Get filtered and ordered Product queryset."""
        queryset = Product.objects.all()

        # Apply filters
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Price range filters with error handling
        for price_param, lookup in [("min_price", "price__gte"), ("max_price", "price__lte")]:
            price_value = request.query_params.get(price_param)
            if price_value:
                try:
                    queryset = queryset.filter(**{lookup: float(price_value)})
                except (ValueError, TypeError):
                    pass  # Ignore invalid price values

        return queryset.order_by("name")

    def list(self, request):
        """List products with pagination and filtering."""
        queryset = self.get_queryset(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieve a specific product by ID."""
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def create(self, request):
        """Create a new product (admin only)."""
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Update an entire product (admin only)."""
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """Partially update a product (admin only)."""
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete a product (admin only)."""
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)