from django.contrib.admin import ModelAdmin, TabularInline, register, site
from food.models import Ingredients, Recipe, RecipeIngredients, Tag

site.site_header = 'Администрирование Foodgram'
EMPTY_VALUE_DISPLAY = 'Значение не указано'


class IngredientInline(TabularInline):
    model = RecipeIngredients
    extra = 2


@register(RecipeIngredients)
class LinksAdmin(ModelAdmin):
    pass


@register(Ingredients)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'pub_date', 'count_in_favourites'
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
    )
    raw_id_fields = ('author', )
    search_fields = (
        'name',
        'author',
        'tags',
    )
    list_filter = (
        'name',
        'author__username',
        'tags__slug',
    )

    inlines = (IngredientInline,)
    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY

    def count_in_favourites(self, obj):
        return obj.is_favorited.all().count()

    count_in_favourites.short_description = 'Общее число в избранном.'


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name', 'color', 'slug',
    )
    search_fields = (
        'name', 'color'
    )
    prepopulated_fields = {"slug": ("name",)}

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY
