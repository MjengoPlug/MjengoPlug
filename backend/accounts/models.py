# from django.db import models
# from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone


# # Create your models here.

# class UserManager(BaseUserManager):
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))
#         return self.create_user(email, password, **extra_fields)
    
#     def create_user(self, email, password, **extra_fields):
#         if not email:
#             raise ValueError(_('The Email must be set'))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user

# class CustomUser(AbstractUser,PermissionError):
#     email = models.EmailField(_('email address'), unique=True)
#     user_name = models.CharField(max_length=150, unique=True)
#     first_name = models.CharField(max_length=150, blank=True)
#     last_name = models.CharField(max_length=150, blank=True)
#     phone_number=models.CharField(max_length=150, blank=True,unique=True)
#     role=models.CharField(max_length=150, blank=True)


#     objects=UserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['user_name','first_name']

    



import random
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

# Custom User Manager
class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(
            email,
            password=password,
            **kwargs
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_number=models.CharField(max_length=150, blank=True,unique=True)
    role=models.CharField(max_length=150, blank=True)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name','first_name', 'last_name']

    def __str__(self):
        return self.email


# OTP Token Model
class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6)  # 6 digit OTP
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    token = models.CharField(max_length=64, default=secrets.token_urlsafe)  # Unique token for OTP

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.otp_expires_at

    def save(self, *args, **kwargs):
        # Ensure otp_code is always set to a 6-digit numeric OTP if it's not already provided
        if not self.otp_code:
            self.otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Generate numeric OTP
        
        # If the token is not already set, generate a new one
        if not self.token:
            self.token = secrets.token_urlsafe()
        
        super().save(*args, **kwargs)  # Save the OTP instance
