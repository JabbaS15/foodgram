from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from food.models import Tag, Ingredients, Recipe, RecipeIngredients
from users.models import CustomUser, Follow
from users.serializers import UserRegistationSerializer


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

    def validate_following(self, value):
        """Валидатор поля validate_following"""
        following = get_object_or_404(CustomUser, username=value)
        user = self.context['request'].user
        if user == following:
            raise ValidationError('Вы не можете подписаться на самого себя!')
        return value

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


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Возвращает из БД и создает рецепты"""
    author = UserRegistationSerializer(
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
    # ingredients = SerializerMethodField()
    # is_favorited = SerializerMethodField()
    # is_in_shopping_cart = SerializerMethodField()
    # image = Base64ImageField()

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

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )
