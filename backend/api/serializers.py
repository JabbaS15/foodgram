from django.contrib.auth.password_validation import validate_password
from django.db.models import F
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api.fields import Base64ImageField
from food.models import Tag, Ingredients, Recipe, RecipeIngredients
from users.models import CustomUser
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингридиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class SubscriptionsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для эндпоинта /subscriptions."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSubscriptionSerializer(UserSerializer):
    """Сериализатор для эндпоинта /subscriptions."""
    recipes = SubscriptionsRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

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
        read_only_fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


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
    tags = TagSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    ingredients = SerializerMethodField()
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

    def get_context(self):
        return {'request': self.context}

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта."""
        return obj.ingredients.values('id', 'name', 'measurement_unit',
                                      amount=F('ingredient__amount'))

    def get_image(self, obj):
        if self.context.get('request').is_secure():
            return 'https://' + str(self.context.get('request').
                                    get_host()) + str(obj.image.url)
        return 'http://' + str(self.context.get('request').
                               get_host()) + str(obj.image.url)

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


class CreateAmountSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        required=True
    )
    amount = serializers.IntegerField(
        required=True
    )


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Cоздает рецепты"""
    ingredients = CreateAmountSerializer(
        many=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    image = Base64ImageField()

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

    def validate(self, data):
        """
        Проверка ингридиентов
        к сожалению frontend не ловит ошибки в validate_ingredients
        """
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    'Количество не может быть отрицательным'
                )
            ingredients_set.add(ingredient['id'])
        if len(ingredients_set) != len(ingredients):
            raise serializers.ValidationError(
                'Такой ингредиент уже выбран')

        return data

    def validate_tags(self, value):
        """Проверка Тэгов"""
        if not value:
            raise serializers.ValidationError(
                'Нужно выбрать тэг'
            )
        tags = self.initial_data.get('tags')
        tags_set = set()
        for tag in tags:
            tags_set.add(tag)
        if len(tags_set) != len(tags):
            raise serializers.ValidationError(
                'Такой тэг уже есть'
            )
        return value

    def validate_cooking_time(self, value):
        if int(self.initial_data.get('cooking_time')) <= 0:
            raise serializers.ValidationError(
                'Время не может быть отрицательным'
            )
        return value

    def create_ingredients(self, ingredients, recipe, menu_list):
        """Создаёт ингридиент."""
        for ingredient in ingredients:
            recipe_list = RecipeIngredients(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            )
            menu_list.append(recipe_list)

    def create(self, validated_data):
        """Создаёт рецепт."""
        menu_list = []
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(
            ingredients,
            recipe,
            menu_list
        )
        RecipeIngredients.objects.bulk_create(menu_list)

        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        menu_list = []
        instance.tags.clear()
        RecipeIngredients.objects.filter(recipe=instance).all().delete()
        tags = validated_data.pop('tags')
        for tag in tags:
            instance.tags.add(tag)
        self.create_ingredients(
            validated_data.pop('ingredients'),
            instance,
            menu_list
        )
        RecipeIngredients.objects.bulk_create(menu_list)

        return super().update(instance, validated_data)
