from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (MAX_LENGTH_INGREDIENT_NAME,
                        MAX_LENGTH_MEASUREMENT_UNIT, MAX_LENGTH_RECIPE_NAME,
                        MAX_LENGTH_SHORT_LINK, MAX_LENGTH_TAG, MIN_AMOUNT,
                        MIN_COOKING_TIME)

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TAG,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_LENGTH_TAG,
        unique=True,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_unit'),
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name='Название',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка',
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(MIN_COOKING_TIME),)
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True,
    )
    short_link = models.CharField(
        max_length=MAX_LENGTH_SHORT_LINK,
        verbose_name='Короткая ссылка на рецепт',
        null=True, blank=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name} от автора {self.author}'

    def favorite_count(self):
        return self.favorited_user.count()

    favorite_count.short_description = 'Добавили в избранное'


class IngredientInRecipe(models.Model):
    """Промежуточная модель ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_recipe',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_recipe',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=(MinValueValidator(MIN_AMOUNT),)
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_combination'),
        ]

    def __str__(self):
        return f'{self.ingredient} в рецепте {self.recipe}'


class Favorite(models.Model):
    """Модель рецептов в избранном."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorited_user',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite'),
        ]

    def __str__(self):
        return f'Пользователю {self.user} нравится {self.recipe}'


class ShoppingCart(models.Model):
    """Модель рецептов в корзине."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='in_shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='in_shopping_cart',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart'),
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'
