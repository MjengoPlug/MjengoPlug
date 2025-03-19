# import random
# from django.db.models.signals import post_save
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils import timezone
# from django.dispatch import receiver
# from django.conf import settings
# from .models import OtpToken
# import logging
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.contrib.auth.tokens import default_token_generator

# # Logger for debugging
# logger = logging.getLogger(__name__)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def handle_user_registered(sender, instance, created, **kwargs):
#     if created:
#         logger.debug(f"User registered: {instance.email}")

#         # Skip superusers if you don't want to generate OTPs for them
#         if instance.is_superuser:
#             return

#         # Generate a numeric OTP code (e.g., 6 digits)
#         otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

#         # Create OTP Token
#         otp = OtpToken.objects.create(
#             user=instance,
#             otp_code=otp_code,  # Assign the generated OTP here
#             otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
#         )
#         logger.debug(f"OTP created: {otp.otp_code} for user {instance.email}")

#         # Set the user to inactive until they verify their email
#         instance.is_active = False
#         instance.save()

#         # Prepare the Djoser activation URL
#         uid = urlsafe_base64_encode(str(instance.pk).encode())
#         token = default_token_generator.make_token(instance)
#         activation_url = f"{settings.EMAIL_FRONTEND_PROTOCOL}://{settings.EMAIL_FRONTEND_DOMAIN}/{settings.ACTIVATION_URL.format(uid=uid, token=token)}"

#         # Prepare the email context
#         context = {
#             'user': instance,
#             'otp_code': otp.otp_code,
#             'verification_url': f"http://127.0.0.1:8000/verify-email/{instance.email}",  # Custom OTP verification URL
#             'activation_url': activation_url,  # Djoser activation link
#             'site_name': settings.SITE_NAME,
#         }

#         # Render the email message from the template
#         subject = "Email Verification"
#         message = render_to_string('email/verification.html', context)

#         # Sender and receiver email addresses
#         sender_email = settings.DEFAULT_FROM_EMAIL
#         receiver_email = [instance.email]

#         logger.debug(f"Sending email to {instance.email} with subject: {subject}")

#         try:
#             # Send the email using the configured backend (SES or console)
#             send_mail(
#                 subject,
#                 message,
#                 sender_email,
#                 receiver_email,
#                 fail_silently=False,
#             )
#             logger.debug(f"Email sent to {instance.email}")
#         except Exception as e:
#             logger.error(f"Failed to send email to {instance.email}: {str(e)}")

import random
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.utils import timezone
from django.dispatch import receiver
from django.conf import settings
from .models import OtpToken
import logging
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Logger for debugging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_user_registered(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"User registered: {instance.email}")

        # Skip superusers if you don't want to generate OTPs for them
        if instance.is_superuser:
            return

        # Generate a numeric OTP code (e.g., 6 digits)
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

        # Create OTP Token
        otp_token = OtpToken.objects.create(
            user=instance,
            otp_code=otp_code,  # Assign the generated OTP here
            otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )
        logger.debug(f"OTP created: {otp_code} for user {instance.email}")

        # Set the user to inactive until they verify their email
        instance.is_active = False
        instance.save()

        # Prepare the Djoser activation URL (link-based verification)
        uid = urlsafe_base64_encode(str(instance.pk).encode())
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.EMAIL_FRONTEND_PROTOCOL}://{settings.EMAIL_FRONTEND_DOMAIN}/{settings.ACTIVATION_URL.format(uid=uid, token=token)}"

        # Prepare the email context (include both OTP code and the OTP token)
        context = {
            'user': instance,
            'otp_code': otp_code,  # OTP code
            'otp_token': otp_token.token,  # The token that identifies this OTP
            'activation_url': activation_url,  # Djoser activation link
            'site_name': settings.SITE_NAME,
        }

        # Render the email message from the template
        subject = "Your OTP and Email Verification"
        message = f"Hi {instance.email},\n\nYour OTP is {otp_code}. It will expire in 5 minutes.\n\n" \
                  f"Use the following OTP token to verify your email: {otp_token.token}\n\n" \
                  f"Alternatively, you can verify your email by clicking the link below:\n{activation_url}\n\nBest,\nTeam"

        # Sender and receiver email addresses
        sender_email = settings.DEFAULT_FROM_EMAIL
        receiver_email = [instance.email]

        logger.debug(f"Sending email to {instance.email} with subject: {subject}")

        try:
            # Send the email using the configured backend (SES or console)
            send_mail(subject, message, sender_email, receiver_email, fail_silently=False)
            logger.debug(f"Email sent to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {instance.email}: {str(e)}")
