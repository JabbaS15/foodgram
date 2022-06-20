from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import CustomUser

CHOICES = (
    ('кг', 'kg'),
    ('г', 'gm'),
    ('л', 'l'),
    ('мл', 'ml'),
    ('шт', 'pc'),
)


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        verbose_name='Название тэга',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='HEX код',
        max_length=7,
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.slug}'


class Ingredients(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=10,
        choices=CHOICES,
        default='gm',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепты',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe_image/',
        blank=True,
    )
    is_favorited = models.ManyToManyField(
        CustomUser,
        verbose_name='Понравившиеся рецепты',
        related_name='is_favorited',
    )
    is_in_shopping_cart = models.ManyToManyField(
        CustomUser,
        related_name='is_in_shopping_cart',
        verbose_name='Список покупок',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredients',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(600)],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author}, {self.name}'


class RecipeIngredients(models.Model):
    """Модель промежуточная для ingredients и amount."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Используется в рецптах',
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в связке',
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )

    def __str__(self):
        return f'{self.amount} {self.ingredients}'

