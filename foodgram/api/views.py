from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientsFilter
from api.pagination import CustomPagination
from api.permissions import AdminOnly, ReadOnly, AuthorOrReadOnly
from api.serializers import TagSerializer, \
    IngredientsSerializer, ChangePasswordSerializer, \
    SubscriptionsRecipeSerializer, ListRecipeSerializer, CreateRecipeSerializer
from food.models import Tag, Ingredients, Recipe, RecipeIngredients


class TagViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает тэги"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly | AdminOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class IngredientsViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает ингридиенты"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [ReadOnly | AdminOnly]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает рецепты"""
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnly | AdminOnly]
    add_serializer = SubscriptionsRecipeSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ListRecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = ListRecipeSerializer(
            instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        serializer = ListRecipeSerializer(
            instance,
            context={'request': self.request}
        )

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        favorite = user.is_favorited
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = favorite.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            favorite.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            favorite.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

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
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        cart = user.is_in_shopping_cart
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = self.add_serializer(
            obj, context={'request': self.request})
        obj_exist = cart.filter(id=pk).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            cart.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            cart.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        user = self.request.user

        if not user.is_in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredients.objects.filter(
            recipe__in=(user.is_in_shopping_cart.values('id'))
        ).values(
            ingredient=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')).annotate(
            amount=Sum('amount')
        )
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для: {user.first_name}'
            f'{datetime.now().strftime("shopping_cart")}'
        )
        for ingredient in ingredients:
            shopping_list += (
                f'{ingredient["ingredient"]}: '
                f'{ingredient["amount"]} {ingredient["measure"]}')
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class ChangePasswordViewSet(UpdateAPIView):
    """Обновление пароля"""
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

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
