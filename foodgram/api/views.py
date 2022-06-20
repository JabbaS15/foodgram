from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from api.serializers import SubscriptionsSerializer, TagSerializer, \
    IngredientsSerializer, RecipeSerializer, RecipeIngredientsSerializer
from food.models import Tag, Ingredients, Recipe, RecipeIngredients


class ListCreateOnlyModelViewSet(mixins.CreateModelMixin,
                                 mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    """A viewset that provides, `create`, and `list` actions."""
    pass


class SubscriptionsViewSet(ListCreateOnlyModelViewSet):
    """Возвращает из БД и создает подписки пользователя"""
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        return user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает тэги"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает рецепты"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает ингридиенты"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class RecipeIngredientsSerializerViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredients.objects.all()
    serializer_class = RecipeIngredientsSerializer
