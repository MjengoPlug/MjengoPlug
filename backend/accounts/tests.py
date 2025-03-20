import random
from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import UserAccount, OtpToken


# Override ROOT_URLCONF so that reverse() can find the named URLs defined in accounts/urls.py.
@override_settings(ROOT_URLCONF='accounts.urls')
class UserAccountTests(TestCase):
    def setUp(self):
        self.email = 'Test@Example.Com'
        self.password = 'testpassword'
        self.user_data = {
            'user_name': 'testuser',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user_normalizes_email(self):
        user = UserAccount.objects.create_user(email=self.email, password=self.password, **self.user_data)
        self.assertEqual(user.email, self.email.lower())
    
    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            UserAccount.objects.create_user(email=None, password=self.password, **self.user_data)

    def test_user_str_returns_email(self):
        user = UserAccount.objects.create_user(email=self.email, password=self.password, **self.user_data)
        self.assertEqual(str(user), user.email)


@override_settings(ROOT_URLCONF='accounts.urls')
class OtpTokenModelTests(TestCase):
    def setUp(self):
        self.user = UserAccount.objects.create_user(
            email='otpuser@example.com',
            password='testpassword',
            user_name='otpuser',
            first_name='OTP',
            last_name='User'
        )
    
    def test_otp_is_not_expired_initially(self):
        otp_token = OtpToken.objects.create(
            user=self.user,
            otp_code='123456',
            otp_expires_at=timezone.now() + timedelta(minutes=5)
        )
        self.assertFalse(otp_token.is_expired())
    
    def test_otp_is_expired_after_expiry(self):
        otp_token = OtpToken.objects.create(
            user=self.user,
            otp_code='123456',
            otp_expires_at=timezone.now() - timedelta(minutes=1)
        )
        self.assertTrue(otp_token.is_expired())


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', ROOT_URLCONF='accounts.urls')
class OtpVerificationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user and an OTP token for verification.
        self.user = UserAccount.objects.create_user(
            email='verifyuser@example.com',
            password='testpassword',
            user_name='verifyuser',
            first_name='Verify',
            last_name='User'
        )
        # Initially set the user to inactive.
        self.user.is_active = False
        self.user.save()
        
        self.otp_code = '654321'
        # Set expiration in the future.
        self.otp_token_obj = OtpToken.objects.create(
            user=self.user,
            otp_code=self.otp_code,
            otp_expires_at=timezone.now() + timedelta(minutes=5)
        )
        self.verify_url = reverse('otp-verify')

    def test_verify_correct_otp(self):
        data = {
            'otp_code': self.otp_code,
            'otp_token': self.otp_token_obj.token,
        }
        response = self.client.post(self.verify_url, data, format='json')
        self.user.refresh_from_db()

        # Check that the user is now active.
        self.assertTrue(self.user.is_active)
        # Verify response status and that JWT tokens are included.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        # Check that cookies are set.
        self.assertIn('access', response.cookies)
        self.assertIn('refresh', response.cookies)

    def test_verify_wrong_otp(self):
        data = {
            'otp_code': '000000',  # incorrect OTP
            'otp_token': self.otp_token_obj.token,
        }
        response = self.client.post(self.verify_url, data, format='json')
        # User should remain inactive.
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), "Invalid OTP.")

    def test_verify_expired_otp(self):
        # Update the OTP to be expired.
        self.otp_token_obj.otp_expires_at = timezone.now() - timedelta(minutes=1)
        self.otp_token_obj.save()

        data = {
            'otp_code': self.otp_code,
            'otp_token': self.otp_token_obj.token,
        }
        response = self.client.post(self.verify_url, data, format='json')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), "OTP has expired. Please request a new one.")


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', ROOT_URLCONF='accounts.urls')
class OtpResendViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resend_url = reverse('otp-resend')
        # Create an inactive user for whom OTP verification is pending.
        self.user = UserAccount.objects.create_user(
            email='resenduser@example.com',
            password='testpassword',
            user_name='resenduser',
            first_name='Resend',
            last_name='User'
        )
        self.user.is_active = False
        self.user.save()
        # Clear the outbox since the signal might have already sent an email.
        mail.outbox = []

    def test_resend_otp_success(self):
        data = {'email': self.user.email}
        response = self.client.post(self.resend_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("otp_token", response.data)
        self.assertEqual(response.data.get("detail"), "A new OTP has been sent to your email.")
        # Check that an email was sent.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Your OTP for Email Verification", mail.outbox[0].subject)

    def test_resend_otp_user_not_found(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.resend_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "User not found.")

    def test_resend_otp_already_verified(self):
        # Mark the user as active.
        self.user.is_active = True
        self.user.save()

        data = {'email': self.user.email}
        response = self.client.post(self.resend_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("detail"), "User is already verified.")
