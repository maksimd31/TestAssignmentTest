from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit products.

    - Authenticated users can read (GET, HEAD, OPTIONS)
    - Only admin users (is_staff=True) can write (POST, PUT, PATCH, DELETE)
    """

    def has_permission(self, request, view):
        """
        Check if user has permission to access the view.

        Args:
            request: The HTTP request object
            view: The view being accessed

        Returns:
            bool: True if permission granted, False otherwise
        """
        # Allow read permissions for authenticated users
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return bool(request.user and request.user.is_authenticated)

        # Write permissions only for admin users
        return bool(request.user and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)