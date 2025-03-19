from django.urls import path, re_path
from .views import (
    CustomProviderAuthView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    OtpVerificationView,
    OtpResendView,
)

urlpatterns = [
        re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='provider-auth'
    ),
    # JWT Token Authentication Views
    path('jwt/create/', CustomTokenObtainPairView.as_view(), name='token_create'),
    path('jwt/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', CustomTokenVerifyView.as_view(), name='token_verify'),

    # Logout View (removes access and refresh cookies)
    path('logout/', LogoutView.as_view(), name='logout'),

    # OTP Views
    path('otp/verify/', OtpVerificationView.as_view(), name='otp-verify'),  # OTP verification endpoint
    path('otp/resend/', OtpResendView.as_view(), name='otp-resend'),  # OTP resend endpoint
]