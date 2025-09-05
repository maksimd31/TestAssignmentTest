from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ProductViewSet

app_name = 'shop'

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
]
