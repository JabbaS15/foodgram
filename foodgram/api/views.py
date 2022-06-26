from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import viewsets, status, mixins
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.serializers import SubscriptionsSerializer, TagSerializer, \
    IngredientsSerializer, RecipeSerializer, RecipeIngredientsSerializer, \
    ChangePasswordSerializer
from food.models import Tag, Ingredients, Recipe, RecipeIngredients


class ListCreateOnlyModelViewSet(mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    """A viewset that provides, `create`, and `list` actions."""
    pass


class UpdateModelViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """A viewset that provides, `update` actions."""
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


class ChangePasswordViewSet(UpdateAPIView):
    """Обновление пароля"""
    serializer_class = ChangePasswordSerializer
    permission_classes = (AllowAny,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                new_password = serializer.data.get("new_password")
                if new_password != serializer.data.get("current_password"):
                    return Response(
                        {"Error": ["Проверьте правильность ввода паролей"]},
                                    status=status.HTTP_400_BAD_REQUEST
                    )
                validate_password(new_password, self.request.user)
                self.object.set_password(new_password)
                self.object.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except exceptions.ValidationError as error:
                return Response(
                    {'status': error}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
