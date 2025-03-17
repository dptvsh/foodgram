from random import choices
from string import ascii_letters, digits

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.serializers import RecipeMinifiedSerializer

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, IngredientInRecipe, Recipe, Tag
from .pagination import RecipePagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('get',)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    http_method_names = ('get',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов с дополнительными действиями."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(
        detail=True,
        permission_classes=[AllowAny],
        url_path='get-link',
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.short_link is None:
            link = None
            while Recipe.objects.filter(short_link=link).exists():
                link = ''.join(choices(
                    population=(ascii_letters + digits), k=3,
                ))
            recipe.short_link = link
            recipe.save()
        url = f'/s/{recipe.short_link}/'
        return Response(
            {'short-link': request.build_absolute_uri(url)},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = user.favorite_recipes.filter(recipe_id=recipe.id)
        if request.method == 'POST':
            if favorite.exists():
                return Response(
                    {'detail': 'Рецепт уже находится в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.favorite_recipes.create(
                user=user,
                recipe=recipe,
            )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not favorite.exists():
            return Response(
                {'detail': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        in_cart = user.in_shopping_cart.filter(recipe_id=recipe.id)
        if request.method == 'POST':
            if in_cart.exists():
                return Response(
                    {'detail': 'Рецепт уже находится в корзине!'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.in_shopping_cart.create(
                user=user,
                recipe=recipe,
            )
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not in_cart.exists():
            return Response(
                {'detail': 'Рецепта нет в списке покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = IngredientInRecipe.objects.select_related(
            'recipe',
        ).filter(
            recipe__in_shopping_cart__user=user,
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            sum_amount=Sum('amount'),
        )
        if not shopping_list:
            return Response(
                {'detail': 'Список покупок пуст!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ingredients = '\n'.join(
            f'{ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) '
            f'— {ingredient["sum_amount"]}'
            for ingredient in shopping_list
        )
        filename = f'foodgram_shopping_list_{user.username}'
        return HttpResponse(
            ingredients,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename={filename}',
            },
        )


def redirect_short_link(request, link):
    """Перенаправление с короткой ссылки на нужный рецепт."""

    recipe = get_object_or_404(Recipe, short_link=link)
    return HttpResponseRedirect(f'/recipes/{recipe.pk}')
