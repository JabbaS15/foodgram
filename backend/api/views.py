from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import CustomPagination
from api.permissions import AdminOnly, ReadOnly, AuthorOrReadOnly
from api.serializers import (
    CreateRecipeSerializer,
    IngredientsSerializer,
    ListRecipeSerializer,
    TagSerializer, SubscriptionsRecipeSerializer
)
from api.utils import FilterDataset
from food.models import Ingredients, Recipe, Tag


class TagViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает тэги"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [ReadOnly | AdminOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'id'
    # slug


class IngredientsViewSet(viewsets.ModelViewSet):
    """Возвращает из БД и создает ингридиенты"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [ReadOnly | AdminOnly]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet, FilterDataset):
    """Возвращает из БД и создает рецепты"""
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnly | AdminOnly]
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    serializer_class = SubscriptionsRecipeSerializer

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
        methods=('POST', 'DELETE'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk):
        """Работает со списком избранных и со списком покупок."""
        return self.obj_favorite_cart_subscribe(request, pk, self.FAVORITE)

    @action(
        methods=('GET', 'POST', 'DELETE'),
        detail=True,
        permission_classes=[IsAuthenticated, ],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        """Работает со списком покупок."""
        return self.obj_favorite_cart_subscribe(request, pk, self.CART)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        return self.download_shopping_cart_txt(request)
