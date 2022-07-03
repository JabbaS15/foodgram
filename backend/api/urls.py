from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagViewSet,
)
from users.views import UserViewSet

app_name = 'api'
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
