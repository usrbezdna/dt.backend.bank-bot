from rest_framework import serializers

from app.internal.models.user import User


class TelegramUserSerializer(serializers.ModelSerializer):
    """
    Serializer for Telegram User model.
    """

    class Meta:
        model = User
        fields = ["tlg_id", "username", "first_name", "last_name", "phone_number"]
