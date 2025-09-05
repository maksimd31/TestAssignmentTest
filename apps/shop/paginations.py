from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for products.

    Attributes:
        page_size (int): Number of items per page (default: 10)
        page_size_query_param (str): Query parameter name for page size
        max_page_size (int): Maximum allowed page size (100)
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
