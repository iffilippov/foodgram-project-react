from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes import models
from users.models import Subscribe
from .filters import IngredientSearchFilter, RecipeFilterSet
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from . import serializers


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request):
        subscriber = request.subscriber
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        if request.method == 'POST':
            serializer = serializers.FollowSerializer(
                data={
                    'subscriber': subscriber.id,
                    'author': author.id,
                },
                context={'request': request}
            )

            serializer.is_valid(raise_exception=True)
            serializer.save(subscriber=subscriber, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(Subscribe,
                                         subscriber=subscriber,
                                         author=author)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        subscriber = request.subscriber
        queryset = User.objects.filter(followed__user=subscriber)
        pages = self.paginate_queryset(queryset)
        serializer = serializers.FollowShowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(ModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.RecipeSerializer
        return serializers.RecipeCreateSerializer

    def adding(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Такой рецепт уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(models.Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = serializers.RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def deleting(self, model, user, pk):
        object = model.objects.filter(user=user, recipe__id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Такого рецепта не существует'},
                        status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.adding(models.Favourite, request.user, pk)
        return self.deleting(models.Favourite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.adding(models.ShoppingCart, request.user, pk)
        return self.deleting(models.ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
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
