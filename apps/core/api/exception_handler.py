"""
Custom exception handler for DRF API responses.
Provides consistent error format across all API endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.

    Response format:
    {
        "error": true,
        "message": "Human readable error message",
        "status_code": 400,
        "details": {...}  // Optional field-level errors
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_message = "An error occurred"
        details = None

        if isinstance(response.data, dict):
            # Handle DRF validation errors
            if 'detail' in response.data:
                error_message = str(response.data['detail'])
            elif 'non_field_errors' in response.data:
                error_message = response.data['non_field_errors'][0] if response.data['non_field_errors'] else "Validation error"
                details = {k: v for k, v in response.data.items() if k != 'non_field_errors'}
            else:
                # Field-level errors
                error_message = "Validation failed"
                details = {}
                for field, errors in response.data.items():
                    if isinstance(errors, list):
                        details[field] = errors[0] if errors else "Invalid value"
                    else:
                        details[field] = str(errors)
        elif isinstance(response.data, list):
            error_message = response.data[0] if response.data else "An error occurred"

        response.data = {
            'error': True,
            'message': error_message,
            'status_code': response.status_code,
        }

        if details:
            response.data['details'] = details

    return response
