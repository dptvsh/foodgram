import base64
import re

from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кастомный сериализатор для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов с сокращенным количеством полей в профиле."""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для валидации токенов."""

    email = serializers.CharField(
        write_only=True,
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        required=True,
        write_only=True,
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            if not user:
                msg = 'Пользователь не найден.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Поля "email" и "password" обязательны для заполнения.'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя (список и отдельная страница)."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(following__id=obj.id).exists()


class UserRegistrationSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователей."""

    password = serializers.CharField(
        label='Пароль',
        style={"input_type": "password"},
        write_only=True
    )
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя 'me' недопустимо.")
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Некорректное имя пользователя.")
        return value


class UserAvatarSerializer(serializers.ModelSerializer):
    """"Сериализатор для редактирования аватара."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class FollowSerializer(UserSerializer):
    """Сериализатор системы подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar',
        )

    def get_recipes(self, obj):
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', 6,
        ))
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeMinifiedSerializer(instance=recipes, many=True).data


class AddFollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на пользователя."""

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя!',
            )
        ]

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на себя!'
            )
        return data
