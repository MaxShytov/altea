"""
Serializers for authentication API.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.services import RegistrationService


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for User model.
    Used in registration response.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified']
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """

    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password (minimum 8 characters)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm password"
    )
    first_name = serializers.CharField(
        required=True,
        max_length=150,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150,
        help_text="User's last name"
    )
    terms_accepted = serializers.BooleanField(
        required=True,
        help_text="User must accept Terms & Conditions"
    )

    def validate_email(self, value):
        """Check if email is already registered."""
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return email

    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            # Create a temporary user object for validation
            temp_user = User(
                email=self.initial_data.get('email', ''),
                first_name=self.initial_data.get('first_name', ''),
                last_name=self.initial_data.get('last_name', ''),
            )
            validate_password(value, user=temp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_terms_accepted(self, value):
        """Ensure terms are accepted."""
        if not value:
            raise serializers.ValidationError(
                "You must accept the Terms & Conditions to register."
            )
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        """Create user using RegistrationService."""
        # Remove password_confirm as it's not needed for creation
        validated_data.pop('password_confirm')

        user = RegistrationService.register_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            terms_accepted=validated_data['terms_accepted'],
        )
        return user


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification email.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Email address to resend verification to"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower()


class LoginUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data in login response.
    Includes profile fields (stubbed until FR-1.3 Onboarding).
    """

    profile_completed = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_completed', 'language']
        read_only_fields = fields

    def get_profile_completed(self, obj) -> bool:
        """
        Returns onboarding completion status.
        TODO: Update after FR-1.3 Onboarding to read from UserProfile.
        """
        # Stub: Will be replaced with obj.profile.onboarding_completed after FR-1.3
        return False

    def get_language(self, obj) -> str:
        """
        Returns user's preferred language.
        TODO: Update after FR-1.3 Onboarding to read from UserProfile.
        """
        # Stub: Will be replaced with obj.profile.language after FR-1.3
        return 'en'


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns JWT tokens.
    """

    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )

    def validate_email(self, value):
        """Normalize email to lowercase and strip whitespace."""
        return value.lower().strip()

    def validate(self, attrs):
        """
        Validate credentials using AuthenticationService.
        """
        from apps.accounts.services import AuthenticationService, AuthErrorCode

        email = attrs.get('email')
        password = attrs.get('password')

        result = AuthenticationService.authenticate_user(email, password)

        if not result.success:
            if result.error_code == AuthErrorCode.EMAIL_NOT_VERIFIED:
                # Store for view to return 403
                attrs['auth_error'] = {
                    'code': result.error_code,
                    'message': result.error_message,
                }
                attrs['user'] = result.user
                return attrs

            # Invalid credentials -> raise validation error
            raise serializers.ValidationError({
                'non_field_errors': [result.error_message]
            })

        attrs['user'] = result.user
        return attrs


class LoginResponseSerializer(serializers.Serializer):
    """
    Response serializer for login endpoint (OpenAPI documentation).
    """

    access_token = serializers.CharField(help_text="JWT access token")
    refresh_token = serializers.CharField(help_text="JWT refresh token")
    user = LoginUserSerializer(help_text="Authenticated user data")


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Email address to send password reset link to"
    )

    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()
