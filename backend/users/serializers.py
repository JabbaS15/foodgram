from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели CustomUserModels для регистрации пользователей."""
    is_subscribed = SerializerMethodField()

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

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        """Проверка подписки."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.is_subscribed.filter(id=obj.id).exists()

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                f'Имя {value} не может быть использованно')
        if not value.isaplha():
            raise serializers.ValidationError(
                'В username допустимы только буквы.'
            )
        return value.capitalize()
