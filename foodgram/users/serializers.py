from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import CustomUser


class UserRegistationSerializer(serializers.ModelSerializer):
    """Сериализатор модели CustomUserModels для регистрации пользователей."""
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

        validators = [
            UniqueTogetherValidator(
                queryset=CustomUser.objects.all(),
                fields=['username', 'email']
            )
        ]

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя {value} не может быть использованно')
        return value

