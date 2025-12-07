"""
Authentication API URL configuration.
"""

from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    # Password-based authentication
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('me/', views.MeAPIView.as_view(), name='me'),
    path('verify-email/<str:token>/', views.VerifyEmailAPIView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationAPIView.as_view(), name='resend_verification'),
    path('forgot-password/', views.ForgotPasswordAPIView.as_view(), name='forgot_password'),

    # OTP-based authentication (passwordless)
    path('otp/request/', views.OTPRequestAPIView.as_view(), name='otp_request'),
    path('otp/verify/', views.OTPVerifyAPIView.as_view(), name='otp_verify'),
]
