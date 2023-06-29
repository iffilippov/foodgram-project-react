from django.core.validators import RegexValidator
from django.db import models

from foodgram.global_constants import (
    COLOR_NAME_LENGTH,
    INGREDIENT_NAME_LENGTH,
    MEASUREMENT_UNIT_LENGTH,
    RECIPE_NAME_LENGTH, SLUG_LENGTH,
    TAG_NAME_LENGTH
)
from users.models import User


class Tag(models.Model):
    '''
    Реализация модели тегов для рецептов.
    '''
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=TAG_NAME_LENGTH,
        unique=True,
        blank=False,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        default='#3caa3c',
        unique=True,
        max_length=COLOR_NAME_LENGTH,
        validators=[
            RegexValidator(regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                           message='Цвет должен быть в формате HEX')
        ],
        blank=False,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        max_length=SLUG_LENGTH,
        blank=False,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        unique_together = ('name', 'slug')

    def __str__(self):
        return f'Тег - {self.name}'


class Ingredient(models.Model):
    '''
    Реализация модели ингредиента для рецептов.
    '''
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=INGREDIENT_NAME_LENGTH,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения количества/объёма',
        max_length=MEASUREMENT_UNIT_LENGTH,
        blank=False,
        default=None,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name', 'measurement_unit']
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Recipe(models.Model):
    '''
    Реализация модели рецепта.
    '''
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        blank=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_NAME_LENGTH,
        blank=False,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
        help_text='Загрузить изображение',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Текст описания рецепта',
        help_text='Текст описания рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientAmountInRecipe',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Рецепт {self.name}'


class IngredientAmountInRecipe(models.Model):
    '''
    Реализация вспомогательной модели, связывающей ингредиенты,
    их количество и рецепт.
    '''
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество/объем',
        null=False,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_IngredientAmountInRecipe')
        ]

    def __str__(self):
        return f'{self.ingredient} -\
            {self.amount} {self.ingredient.measurement_unit}'


class Favourite(models.Model):
    '''
    Реализация модели избранного.
    '''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favourites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='favourites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    '''
    Реализация модели корзины покупок.
    '''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='shopping_cart',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину покупок {self.recipe}'
