"""
Celery tasks for accounts app.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='accounts.send_otp_email')
def send_otp_email_task(email: str, code: str, language: str = 'en') -> bool:
    """
    Asynchronously send OTP email.

    Args:
        email: Recipient email address.
        code: The 6-digit OTP code.
        language: Language code for email content.

    Returns:
        True if email was sent successfully.
    """
    from apps.accounts.services import OTPService

    try:
        success = OTPService.send_otp_email(email, code, language)
        if success:
            logger.info(f"OTP email sent asynchronously: email={email}")
        else:
            logger.error(f"Failed to send OTP email asynchronously: email={email}")
        return success
    except Exception as e:
        logger.error(f"Error sending OTP email asynchronously: email={email}, error={e}")
        return False


@shared_task(name='accounts.cleanup_expired_otp_tokens')
def cleanup_expired_otp_tokens_task() -> int:
    """
    Periodically clean up expired OTP tokens.

    Should be scheduled to run every 5 minutes via Celery Beat.

    Returns:
        Number of deleted tokens.
    """
    from apps.accounts.services import OTPService

    try:
        deleted_count = OTPService.cleanup_expired_tokens()
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired OTP tokens: error={e}")
        return 0
