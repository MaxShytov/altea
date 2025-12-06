"""
Authentication API URL configuration.
"""

from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('verify-email/<str:token>/', views.VerifyEmailAPIView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationAPIView.as_view(), name='resend_verification'),
]
