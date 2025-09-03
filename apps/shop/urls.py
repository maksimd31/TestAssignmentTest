from django.urls import path
from .views import RegisterAPIView, LoginAPIView

app_name = 'shop'

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
]
