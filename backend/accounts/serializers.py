from rest_framework import serializers

class OtpVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=6)  # The OTP code sent to the user
    otp_token = serializers.CharField(max_length=64)  # The token associated with the OTP

    def validate_otp_code(self, value):
        """Ensure the OTP code is numeric and exactly 6 digits long."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric.")
        if len(value) != 6:
            raise serializers.ValidationError("OTP code must be exactly 6 digits.")
        return value

    def validate_otp_token(self, value):
        """Ensure the OTP token is in the correct format (URL-safe token)."""
        if len(value) < 20 or len(value) > 64:  # A URL-safe token can range between 20 and 64 characters
            raise serializers.ValidationError("Invalid OTP token format. Token length should be between 20 and 64 characters.")
        
        # You can also check for valid characters in a URL-safe base64 token (alphanumeric + '-' + '_')
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        if not all(c in valid_chars for c in value):
            raise serializers.ValidationError("OTP token contains invalid characters. Only alphanumeric characters, '-' and '_' are allowed.")
        
        return value

class OtpResendSerializer(serializers.Serializer):
    email = serializers.EmailField()
