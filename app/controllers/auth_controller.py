from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD

    def validate(self, attrs):

        # Normalize email/username to lowercase for case-insensitive login
        username_value = attrs.get(self.username_field)
        if isinstance(username_value, str):
            username_value = username_value.lower()
            attrs[self.username_field] = username_value

        # Use authenticate to check credentials
        credentials = {
            self.username_field: username_value,
            "password": attrs.get("password"),
        }
        user = authenticate(**credentials)
        if user is None:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid username or password"]}
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["User account is disabled"]}
            )
        data = super().validate(attrs)
        # Add user info to the response as a JSON string to avoid type errors
        data["user"] = user.api_response()
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
