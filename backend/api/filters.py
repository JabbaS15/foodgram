from django_filters import rest_framework

from food.models import Ingredients, Recipe, Tag
from users.models import CustomUser


class IngredientsFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredients
        fields = ('name', )


class RecipesFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = rest_framework.ModelMultipleChoiceFilter(
        field_name='author__username',
        to_field_name='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', )
