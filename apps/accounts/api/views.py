"""
API Views for authentication.
"""

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services import (
    AuthErrorCode,
    EmailVerificationService,
    OTPService,
    PasswordResetService,
)
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    LoginResponseSerializer,
    LoginUserSerializer,
    OTPRequestSerializer,
    OTPResponseSerializer,
    OTPVerifySerializer,
    OTPVerifyResponseSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    UserSerializer,
)
from .throttling import (
    ForgotPasswordThrottle,
    LoginThrottle,
    OTPRequestThrottle,
    OTPVerifyThrottle,
    RegistrationThrottle,
    ResendVerificationThrottle,
)


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


class LoginAPIView(APIView):
    """
    API endpoint for user login.

    Authenticates user with email and password, returns JWT tokens.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                response=LoginResponseSerializer,
                description="Login successful. JWT tokens returned.",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "user": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "email": "user@example.com",
                                "first_name": "Max",
                                "last_name": "Mueller",
                                "profile_completed": False,
                                "language": "en"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error (missing fields)"),
            401: OpenApiResponse(
                description="Invalid credentials",
                examples=[
                    OpenApiExample(
                        "Invalid credentials",
                        value={"detail": "Invalid credentials"}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Email not verified",
                examples=[
                    OpenApiExample(
                        "Email not verified",
                        value={
                            "detail": "Please verify your email",
                            "code": "email_not_verified"
                        }
                    )
                ]
            ),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="User login",
        description="Authenticate user and return JWT tokens.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            # Check if it's an invalid credentials error
            errors = serializer.errors
            non_field_errors = errors.get('non_field_errors', [])

            if non_field_errors and 'Invalid credentials' in non_field_errors:
                return Response(
                    {'detail': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Other validation errors (missing fields, etc.)
            return Response(
                {
                    'error': True,
                    'message': 'Validation failed',
                    'details': errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for email not verified error
        auth_error = serializer.validated_data.get('auth_error')
        if auth_error and auth_error.get('code') == AuthErrorCode.EMAIL_NOT_VERIFIED:
            return Response(
                {
                    'detail': auth_error['message'],
                    'code': auth_error['code'].value,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': LoginUserSerializer(user).data,
            },
            status=status.HTTP_200_OK
        )


class MeAPIView(APIView):
    """
    API endpoint to get current authenticated user.

    Returns the authenticated user's data based on the JWT token.
    Used for session restoration on app startup.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=LoginUserSerializer,
                description="Current user data",
            ),
            401: OpenApiResponse(description="Not authenticated"),
        },
        summary="Get current user",
        description="Returns the currently authenticated user's data.",
        tags=["Authentication"],
    )
    def get(self, request):
        """Return current authenticated user data."""
        return Response(
            LoginUserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):
    """
    API endpoint for requesting password reset.

    Sends a password reset email to the specified address if the account exists.
    Always returns success to prevent email enumeration attacks.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ForgotPasswordThrottle]

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset email sent (if account exists)",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "message": "If an account exists with this email, you will receive password reset instructions."
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="Request password reset",
        description="Request a password reset link to be sent to the specified email address.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

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
        success, message = PasswordResetService.request_reset(email)

        return Response(
            {
                'error': False,
                'message': message,
            },
            status=status.HTTP_200_OK
        )


class OTPRequestAPIView(APIView):
    """
    API endpoint to request an OTP code for login/signup.

    This is the unified authentication flow:
    - If email exists: sends OTP for login
    - If email doesn't exist: sends OTP for registration

    Always returns success to prevent email enumeration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPRequestThrottle]

    @extend_schema(
        request=OTPRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=OTPResponseSerializer,
                description="OTP sent successfully (if email is valid).",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "message": "Verification code sent to your email",
                            "email_masked": "u***@e***.com"
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Validation error (invalid email format)"),
            429: OpenApiResponse(description="Rate limit exceeded (try again in 60s)"),
        },
        summary="Request OTP code",
        description=(
            "Request a 6-digit OTP code to be sent to the specified email address. "
            "This endpoint handles both login and registration - the backend will "
            "automatically create a new user if the email doesn't exist. "
            "Rate limited to 1 request per 60 seconds."
        ),
        tags=["OTP Authentication"],
    )
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)

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
        ip_address = OTPService.get_client_ip(request)

        # Create and send OTP
        success, masked_email = OTPService.create_and_send_otp(email, ip_address)

        return Response(
            {
                'message': 'Verification code sent to your email',
                'email_masked': masked_email,
            },
            status=status.HTTP_200_OK
        )


class OTPVerifyAPIView(APIView):
    """
    API endpoint to verify OTP code and authenticate user.

    On successful verification:
    - If email exists: logs in existing user
    - If email doesn't exist: creates new user and logs them in

    Returns JWT tokens for authenticated user.
    """

    permission_classes = [AllowAny]
    throttle_classes = [OTPVerifyThrottle]

    @extend_schema(
        request=OTPVerifySerializer,
        responses={
            200: OpenApiResponse(
                response=OTPVerifyResponseSerializer,
                description="OTP verified successfully. JWT tokens returned.",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                            "user": {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "email": "user@example.com",
                                "first_name": "",
                                "last_name": "",
                                "profile_completed": False,
                                "language": "en"
                            },
                            "is_new_user": True
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid OTP code or validation error",
                examples=[
                    OpenApiExample(
                        "Invalid code",
                        value={
                            "error": True,
                            "message": "Invalid code. 4 attempt(s) remaining.",
                            "code": "invalid_code",
                            "attempts_remaining": 4
                        }
                    ),
                    OpenApiExample(
                        "Expired code",
                        value={
                            "error": True,
                            "message": "Code expired. Request a new one.",
                            "code": "otp_expired"
                        }
                    ),
                    OpenApiExample(
                        "Max attempts",
                        value={
                            "error": True,
                            "message": "Too many attempts. Request a new code.",
                            "code": "max_attempts"
                        }
                    )
                ]
            ),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
        summary="Verify OTP code",
        description=(
            "Verify the 6-digit OTP code and authenticate the user. "
            "On success, returns JWT access and refresh tokens. "
            "If the email doesn't exist, a new user will be created."
        ),
        tags=["OTP Authentication"],
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)

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
        code = serializer.validated_data['code']

        # Verify OTP
        result = OTPService.verify_otp(email, code)

        if not result.success:
            response_data = {
                'error': True,
                'message': result.error_message,
                'code': result.error_code.value if result.error_code else None,
            }
            if result.attempts_remaining > 0:
                response_data['attempts_remaining'] = result.attempts_remaining

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT tokens
        user = result.user
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': LoginUserSerializer(user).data,
                'is_new_user': result.is_new_user,
            },
            status=status.HTTP_200_OK
        )
