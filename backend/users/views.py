from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.serializers import (AddFollowSerializer, FollowSerializer,
                               TokenObtainSerializer, UserAvatarSerializer,
                               UserSerializer)

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):
    """Кастомный вьюсет для получения токена."""

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
        )


class CustomTokenLogout(views.APIView):
    """Выход пользователя из системы и удаление его токена."""

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет пользователя с дополнительными действиями."""

    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        return Response(
            UserSerializer(
                request.user,
                context={'request': request}
            ).data,
        )

    @action(
        methods=['put', 'delete'],
        detail=False,
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(
                instance=request.user, data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        context = {'request': request}

        if request.method == 'POST':
            serializer = AddFollowSerializer(
                data={
                    'user': user.id,
                    'following': author.id,
                },
                context=context,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        if not user.follower.filter(following_id=author.id).exists():
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.follower.filter(following_id=author.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        followers = User.objects.filter(
            following__user=request.user,
        ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = FollowSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            followers,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)
