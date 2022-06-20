from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views

from api.views import TagViewSet, RecipesViewSet, IngredientsViewSet
from users.views import UserViewSet

app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = (
    path('v1/', include(router_v1.urls)),
    path('auth/token/login/', views.TokenObtainPairView.as_view(),
         name='token_create'),

)

# path('auth/token/login/', views.TokenRefreshView.as_view(),
#      name='token_refresh'),
# path('auth/token/login/', views.TokenVerifyView.as_view(), name='token_verify')