from django.contrib import admin

from . import models


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'get_tags', 'count_favourites')
    list_filter = ('author', 'name', 'tags',)

    def get_tags(self, object):
        return '\n'.join((tag.name for tag in object.tags.all()))

    get_tags.short_description = 'Теги'

    def count_favourites(self, object):
        return object.favourites.count()

    count_favourites.short_description = 'Количество раз в избранном'


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(models.Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(models.IngredientAmountInRecipe)
class IngredientAmountInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
