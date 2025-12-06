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
