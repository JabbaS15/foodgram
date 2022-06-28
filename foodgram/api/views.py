from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, \
    HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from api.permissions import AdminOnly, ReadOnly, AuthorOrReadOnly
from api.serializers import TagSerializer, \
    IngredientsSerializer, ChangePasswordSerializer, \
    SubscriptionsRecipeSerializer, ListRecipeIngredientsAmountSerializer, \
    ListRecipeSerializer, CreateRecipeSerializer
from food.models import Tag, Ingredients, Recipe


class ListCreateOnlyModelViewSet(mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    """A viewset that provides, `create`, and `list` actions."""
    pass


class TagViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает тэги"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly | AdminOnly]


class RecipesViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает рецепты"""
    queryset = Recipe.objects.select_related('author')
    permission_classes = [AuthorOrReadOnly | AdminOnly]
    add_serializer = SubscriptionsRecipeSerializer

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ListRecipeSerializer
        return CreateRecipeSerializer

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса."""
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping in ('1', 'true',):
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping in ('0', 'false',):
            queryset = queryset.exclude(cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ('1', 'true',):
            queryset = queryset.filter(favorite=user.id)
        if is_favorited in ('0', 'false',):
            queryset = queryset.exclude(favorite=user.id)

        return queryset

    @action(
        methods=('GET', 'POST', 'DELETE',),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        """Работает со списком избранных."""

        user = self.request.user

        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        favorite = user.is_favorited
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = favorite.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            favorite.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            favorite.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        methods=('GET', 'POST', 'DELETE',),
        detail=True,
        permission_classes=[IsAuthenticated, ],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        """Работает со списком покупок."""
        user = self.request.user

        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        cart = user.is_in_shopping_cart
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = cart.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            cart.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            cart.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = ListRecipeIngredientsAmountSerializer.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
            f'{datetime.now().strftime("shopping_cart")}\n\n'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient"]}: {ingredient["amount"]} {ingredient["measure"]}\n')
        shopping_list += '\n\nПосчитано в Foodgram'
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class IngredientsViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает ингридиенты"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [ReadOnly | AdminOnly]


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
