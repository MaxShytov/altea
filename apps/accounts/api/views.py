"""
API Views for authentication.
"""

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.services import EmailVerificationService
from .serializers import RegisterSerializer, ResendVerificationSerializer, UserSerializer
from .throttling import RegistrationThrottle, ResendVerificationThrottle


class RegisterAPIView(APIView):
    """
    API endpoint for user registration.

    Creates a new user account and sends a verification email.
    The user must verify their email before they can log in.
    """

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationThrottle]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                description="User registered successfully. Verification email sent."
            ),
            400: OpenApiResponse(description="Validation error"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="Register a new user",
        description="Create a new user account. A verification email will be sent.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'error': True,
                    'message': 'Validation failed',
                    'details': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        return Response(
            {
                'error': False,
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )


class VerifyEmailAPIView(APIView):
    """
    API endpoint for email verification.

    This endpoint returns an HTML page (not JSON) as it's accessed
    via email link in a browser.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="HTML verification result page"),
        },
        summary="Verify email address",
        description="Verify user's email address using the token from verification email.",
        tags=["Authentication"],
    )
    def get(self, request, token):
        success, message, user = EmailVerificationService.verify_token(token)

        context = {
            'success': success,
            'message': message,
            'user': user,
            'show_resend': not success and user is not None,
        }

        return render(request, 'accounts/verify_email.html', context)


class ResendVerificationAPIView(APIView):
    """
    API endpoint to resend verification email.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResendVerificationThrottle]

    @extend_schema(
        request=ResendVerificationSerializer,
        responses={
            200: OpenApiResponse(description="Verification email sent (if email exists)"),
            400: OpenApiResponse(description="Email already verified or validation error"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="Resend verification email",
        description="Resend the verification email to the specified address.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'error': True,
                    'message': 'Validation failed',
                    'details': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        success, message = EmailVerificationService.resend_verification(email)

        if success:
            return Response(
                {
                    'error': False,
                    'message': message,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'error': True,
                    'message': message,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
