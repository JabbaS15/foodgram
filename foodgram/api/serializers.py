from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Ingredients, Recipe, RecipeIngredients
from users.models import CustomUser, Follow
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""
    class Meta:
        model = Ingredients
        fields = '__all__'


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для папещиков"""
    user = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=CurrentUserDefault()
    )
    following = SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username',
    )

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Нельзя подписаться на автора повторно!'
            )
        ]

    def validate_following(self, value):
        """Валидатор поля validate_following"""
        following = get_object_or_404(CustomUser, username=value)
        user = self.context['request'].user
        if user == following:
            raise ValidationError('Вы не можете подписаться на самого себя!')
        return value


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ingredients и amount."""
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Возвращает из БД и создает рецепты"""
    author = UserSerializer(
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = IngredientsSerializer(
        many=True,
        read_only=True
    )
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_is_favorited(self, obj):
        """Проверка избранного"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_favorited.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка списка покупок"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_in_shopping_cart.filter(id=obj.id).exists()


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для эндпоинта /subscriptions."""

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__'


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор для эндпоинта /subscriptions."""
    recipes = SubscriptionsRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для смены пароля"""
    new_password = serializers.CharField(max_length=150, required=True)
    current_password = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = CustomUser
        fields = ('new_password', 'current_password')

    @staticmethod
    def validate_new_password(value):
        validate_password(value)
        return value
