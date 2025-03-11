from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OtpToken
from .serializers import OtpVerificationSerializer, OtpResendSerializer
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.social.views import ProviderAuthView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.conf import settings
from rest_framework.permissions import AllowAny
import random

class OtpVerificationView(APIView):
    authentication_classes = []  # Disable authentication since email is not verified
    permission_classes = []  # You can use AllowAny to allow unverified users

    def post(self, request, *args, **kwargs):
        serializer = OtpVerificationSerializer(data=request.data)

        # Ensure that the serializer is valid
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            otp_token = serializer.validated_data['otp_token']  # The OTP token

            # Fetch the OTP token from the database
            try:
                otp = OtpToken.objects.get(token=otp_token)
            except OtpToken.DoesNotExist:
                return Response({"detail": "Invalid or expired OTP token."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate the OTP code
            if otp.otp_code != otp_code:
                return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the OTP is expired
            if otp.is_expired():
                return Response({"detail": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the user after successful OTP verification
            user = otp.user  # Retrieve the user associated with the OTP
            user.is_active = True
            user.save()

            # Optionally, issue JWT tokens after email verification
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Respond with success and include the tokens
            response = Response({
                "detail": "Email verified successfully!",
                "access": access_token,
                "refresh": refresh_token
            })

            # Optionally, set the JWT tokens in cookies
            response.set_cookie(
                'access', access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh', refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

            return response

        # If the serializer is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OtpResendView(APIView):
    authentication_classes = []  # Disable authentication since email is not verified
    permission_classes = []  # You can use AllowAny to allow unverified users
    def post(self, request, *args, **kwargs):
        serializer = OtpResendSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check if user exists
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user is already active
            if user.is_active:
                return Response({"detail": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate a new OTP and create the OTP token
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            otp_token = OtpToken.objects.create(
                user=user, 
                otp_code=otp_code,
                otp_expires_at=timezone.now() + timezone.timedelta(minutes=5)
            )

            # Send OTP to email
            subject = "Your OTP for Email Verification"
            message = f"Hi {user.username},\n\nYour OTP is {otp_code}. It will expire in 5 minutes.\n\nBest,\nTeam"
            send_mail(subject, message, 'learnerviner@gmail.com', [user.email])

            return Response({"detail": "A new OTP has been sent to your email.", "otp_token": otp_token.token}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response