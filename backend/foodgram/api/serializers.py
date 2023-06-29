from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    SerializerMethodField,
    SlugRelatedField,
    ValidationError
)

from recipes import models
from users.models import Subscribe, User
from .fields import Base64ImageField


class CustomUserSerializer(UserSerializer):
    '''
    Сериализатор объектов типа кастомный пользователь.
    '''
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return False if not request or request.user.is_anonymous else \
            Subscribe.objects.filter(
                subscriber=request.user, author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    '''
    Сериализатор для создания объектов типа кастомный пользователь.
    '''
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise ValidationError({
                'errors': f'Имя пользователя {value} недопустимо',
            })
        return value


class SubscriptionSerializer(ModelSerializer):
    '''
    Сериализатор объектов модели подписок.
    '''
    class Meta:
        model = Subscribe
        fields = ('subscriber', 'author')

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].user == data['author']:
            raise ValidationError({
                'errors': 'Подписка на себя запрещена.',
            })
        return data


class SubscriptionShowSerializer(ModelSerializer):
    '''
    Сериализатор отображения подписок.
    '''
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, author):
        return models.Recipe.objects.filter(author=author).count()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        recipes = models.Recipe.objects.filter(author=author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serialiser = RecipeShortSerializer(
            recipes,
            many=True,
            context={'request': queryset}
        )
        return serialiser.data

    def get_is_subscribed(self, author):
        return Subscribe.objects.filter(
            subscriber=self.context.get('request').user,
            author=author
        ).exists()


class TagSerializer(ModelSerializer):
    '''
    Сериализатор объектов типа Тег.
    '''
    class Meta:
        model = models.Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(ModelSerializer):
    '''
    Сериализатор объектов типа Ингредиент.
    '''
    class Meta:
        model = models.Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeShortSerializer(ModelSerializer):
    '''
    Сериализатор для получения информации о рецепте.
    '''
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeIngredientsSerializer(ModelSerializer):
    '''
    Сериализатор для получение информации об ингредиентах в рецепте.
    '''
    id = PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = models.IngredientAmountInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(ModelSerializer):
    '''
    Сериализатор объектов типа Рецепт.
    '''
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        read_only=True,
        source='ingredient_list',
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return False if request.user.is_anonymous else \
            models.Favourite.objects.filter(
                user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return False if request.user.is_anonymous else \
            models.ShoppingCart.objects.filter(
                user=request.user, recipe__id=obj.id).exists()


class CreateIngredientRecipeSerializer(ModelSerializer):
    '''
    Сериализатор для добавления ингредиента в рецепт.
    '''
    id = PrimaryKeyRelatedField(
        source='ingredient',
        queryset=models.Ingredient.objects.all()
    )

    class Meta:
        model = models.IngredientAmountInRecipe
        fields = (
            'id',
            'amount',
        )

    def validate_amount(self, data):
        if int(data) < 1:
            raise ValidationError({
                'ingredients': (
                    'Количество должно быть больше 1'
                ),
                'msg': data
            })
        return data


class RecipeCreateSerializer(ModelSerializer):
    '''
    Сериализатор для создания или обновления рецепта.
    '''
    image = Base64ImageField(use_url=True, max_length=None)
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateIngredientRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(), many=True
    )
    cooking_time = IntegerField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create_ingredients(self, recipe, ingredients):
        models.IngredientAmountInRecipe.objects.bulk_create([
            models.IngredientAmountInRecipe(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])
        return recipe

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise ValidationError(
                    'Есть задублированные ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        if data['cooking_time'] < 1:
            raise ValidationError(
                'Время приготовления должно быть больше 0!'
            )
        return data

    @atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(
            author=user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = instance
        models.IngredientAmountInRecipe.objects.filter(recipe=recipe).delete()
        self.create_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data
