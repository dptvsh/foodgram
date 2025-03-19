from django.core.validators import MinValueValidator
from rest_framework import serializers

from recipes.constants import MIN_AMOUNT
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.serializers import Base64ImageField, UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для общей работы с ингредиентами."""

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'measurement_unit',
        )


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами в пределах рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class CreateUpdateIngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления ингредиентов в рецепте."""

    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True,
        validators=(MinValueValidator(MIN_AMOUNT),),
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id', 'recipe', 'amount',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'slug',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipe',
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorite_recipes.filter(recipe_id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.in_shopping_cart.filter(recipe_id=obj.id).exists()
        return False


class RecipeCreateSerializer(RecipeListSerializer):
    """Сериализатор создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = CreateUpdateIngredientInRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Добавьте как минимум один тег!'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться!'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте как минимум один ингредиент!'
            )
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(ingredient['id'])
        if len(ingredient_list) != len(set(ingredient_list)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )
        return ingredients

    def _create_ingredients(self, recipe, ingredients):
        ingredients_list = [
            IngredientInRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(
            ingredients_list,
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is None:
            raise serializers.ValidationError(
                'Вы забыли про ингредиенты!'
            )
        if tags is None:
            raise serializers.ValidationError(
                'Вы забыли про теги!'
            )
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context,
        ).data
