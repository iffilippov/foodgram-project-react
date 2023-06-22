from django.core.validators import RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[a-zA-Z]{1}[-a-zA-Z0-9_]+$',
                           message='Тег должен состоять из букв и цифр')
        ],
        blank=False,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        default='#3caa3c',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                           message='Цвет должен быть в формате HEX')
        ],
        blank=False,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        max_length=150,
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
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150,
        blank=False,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения количества/объёма',
        max_length=150,
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        blank=False,
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
        blank=False,
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
        help_text='Загрузить изображение',
        blank=False,
    )
    text = models.TextField(
        verbose_name='Текстовое описание',
        help_text='Текстовое описание рецепта',
        blank=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientToRecipe',
        verbose_name='Ингредиенты',
        blank=False,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientToRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        null=False,
        verbose_name='Количество/объем',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_list',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_IngredientToRecipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Рецепт в корзине покупок'
        verbose_name_plural = 'Рецепты в корзине покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину покупок {self.recipe}'
