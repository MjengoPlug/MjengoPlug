# email.py

from templated_mail.mail import BaseEmailMessage
from djoser import utils
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator


class OtpEmail(BaseEmailMessage):
    template_name = "email/otp_verification.html"  # Customize your template name here

    def get_context_data(self):
        context = super().get_context_data()

        user = context.get("user")
        otp_code = context.get("otp_code")
        otp_expires_at = context.get("otp_expires_at")

        context["uid"] = utils.encode_uid(user.pk)
        context["otp_code"] = otp_code
        context["otp_expires_at"] = otp_expires_at
        context["url"] = settings.OTP_VERIFICATION_URL.format(**context)  # Customize your URL format if necessary

        return context
