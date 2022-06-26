from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet, RecipesViewSet, IngredientsViewSet, ChangePasswordViewSet
from users.views import UserViewSet

app_name = 'api'
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = (
    path('', include(router.urls)),
    path(r'set_password/', ChangePasswordViewSet.as_view(), name='set_password'),
    path(r'auth/', include('djoser.urls.authtoken')),
)


