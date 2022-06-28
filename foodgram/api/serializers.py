import os
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from foodgram.settings import MEDIA_ROOT
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault, SerializerMethodField
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from food.models import Tag, Ingredients, Recipe, RecipeIngredients
from users.models import CustomUser
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


class CreateRecipeIngredientsAmountSerializer(serializers.Serializer):
    """Создание связи для ingredients и amount."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(required=True)


class ListRecipeIngredientsAmountSerializer(serializers.ModelSerializer):
    """Получение списка для ingredients и amount."""
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    @staticmethod
    def get_id(obj):
        return obj.ingredient.id

    @staticmethod
    def get_name(obj):
        return obj.ingredient.name

    @staticmethod
    def get_measurement_unit(obj):
        return obj.ingredient.measurement_unit

    @staticmethod
    def get_amount(obj):
        return obj.amount


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для эндпоинта /subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


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


class ListRecipeSerializer(serializers.ModelSerializer):
    """Возвращает рецепты"""
    author = UserSerializer(read_only=True)
    ingredients = ListRecipeIngredientsAmountSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        """Запрос картинки"""
        return (
                'http://' + str(self.context.get('request').get_host()) +
                str(obj.image.url)
        )

    def get_is_favorited(self, obj):
        """Запрос избранного"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_favorited.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Запрос списка покупок"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.is_in_shopping_cart.filter(id=obj.id).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Cоздает рецепты"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    ingredients = CreateRecipeIngredientsAmountSerializer(
        many=True,
        required=True,
    )
    # image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    # def validate_ingredients(self, value):
    #     if not value:
    #         raise serializers.ValidationError(
    #             'Ingredients field may not be blank.'
    #         )
    #
    #     validation_errors = []
    #
    #     result = {}
    #     for item in value:
    #         if item['amount'] < 1:
    #             validation_errors.append(
    #                 f'Ensure amount of {item["id"].name} '
    #                 f'is greater than or equal to 1.'
    #             )
    #
    #         if item['id'] in result:
    #             result[item['id']] += item['amount']
    #         else:
    #             result[item['id']] = item['amount']
    #
    #     if validation_errors:
    #         raise serializers.ValidationError(validation_errors)
    #
    #     validated_data = []
    #     for key in result:
    #         validated_data.append(
    #             {
    #                 'id': key,
    #                 'amount': result[key]
    #             }
    #         )
    #
    #     return validated_data
    #
    # def validate_tags(self, value):
    #     if not value:
    #         raise serializers.ValidationError('Tags field may not be blank.')
    #     return value
    #
    # def create(self, validated_data):
    #     """Создаёт рецепт."""
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(author=self.context.get(
    #         'request'
    #     ).user, **validated_data)
    #     recipe.tags.set(tags)
    #     recipe.save()
    #     for elem in ingredients:
    #         ingredient = elem.pop('id')
    #         RecipeIngredients.objects.create(
    #             recipe=recipe,
    #             ingredients=ingredient,
    #             **elem
    #         )
    #     return recipe
    #
    # def update(self, instance, validated_data):
    #     instance.text = validated_data.get('text', instance.text)
    #     if 'tags' in validated_data:
    #         instance.tags.set(validated_data['tags'])
    #
    #     instance.cooking_time = validated_data.get(
    #         'cooking_time',
    #         instance.cooking_time
    #     )
    #     instance.name = validated_data.get('name', instance.name)
    #     if 'image' in validated_data:
    #         try:
    #             os.remove(MEDIA_ROOT + '/' + str(instance.image))
    #         except PermissionError:
    #             pass
    #         instance.image = validated_data['image']
    #     instance.save()
    #
    #     if 'ingredients' in validated_data:
    #         instance.recipe_ingredients.all().delete()
    #         ingredients = validated_data.get('ingredients')
    #         for elem in ingredients:
    #             ingredient = elem.pop('id')
    #             RecipeIngredients.objects.create(
    #                 recipe=instance,
    #                 ingredient=ingredient,
    #                 **elem
    #             )
    #     return instance
