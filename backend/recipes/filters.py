from django_filters import rest_framework as custom_filter

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(custom_filter.FilterSet):
    """Кастомный фильтр для рецептов."""

    is_favorited = custom_filter.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = custom_filter.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )
    tags = custom_filter.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated and value:
            return queryset.none()
        if value:
            return queryset.filter(favorited_user__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated and value:
            return queryset.none()
        if value:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset


class IngredientFilter(custom_filter.FilterSet):
    """Кастомный фильтр для ингредиентов."""

    name = custom_filter.CharFilter(
        method='filter_name',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            name__icontains=value,
        ).order_by('name')
