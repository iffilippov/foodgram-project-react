from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes import models
from users.models import Subscribe, User
from . import serializers
from .filters import IngredientSearchFilter, RecipeFilterSet
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly


class CustomUserViewSet(UserViewSet):
    '''
    Вьюсет для создания модели кастомного пользователя.
    '''
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        subscriber = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = serializers.SubscriptionSerializer(
                data={
                    'subscriber': subscriber.id,
                    'author': author.id,
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                subscriber=subscriber,
                author=author
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        subscription = get_object_or_404(
            Subscribe,
            subscriber=request.user,
            author=author
        )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(author__subscriber=subscriber)
        pages = self.paginate_queryset(queryset)
        serializer = serializers.SubscriptionShowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    '''
    Вьюсет для создания тегов.
    '''
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(ModelViewSet):
    '''
    Вьюсет для создания ингредиентов.
    '''
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    '''
    Вьюсет для создания рецептов.
    '''
    queryset = models.Recipe.objects.all()
    permission_classes = (
        IsAuthorOrAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return serializers.RecipeSerializer
        return serializers.RecipeCreateSerializer

    def add_recipe(self, model, user, pk):
        recipe = get_object_or_404(models.Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = serializers.RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, pk):
        object = model.objects.filter(user=user, recipe__id=pk)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(models.Favourite, request.user, pk)
        return self.delete_recipe(models.Favourite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_recipe(models.ShoppingCart, request.user, pk)
        return self.delete_recipe(models.ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = models.IngredientAmountInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount_sum=Sum('amount'))

        today = timezone.now()
        shopping_card_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%d.%m.%Y}\n'
        )
        shopping_card_list += '\n'.join([
            f'+ {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["amount_sum"]}'
            for ingredient in ingredients
        ])
        shopping_card_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_card_list.txt'
        response = HttpResponse(shopping_card_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
