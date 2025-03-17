from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = ('name',)
    ordering = ('name',)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug',
    )
    search_fields = (
        'name', 'slug',
    )
    ordering = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'display_tags', 'favorite_count'
    )
    search_fields = (
        'name', 'author__username',
    )
    list_filter = ('tags',)
    ordering = ('-pub_date',)
    inlines = (
        IngredientInRecipeInline,
    )

    def display_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    display_tags.short_description = 'Теги'
