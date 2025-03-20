from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME


class CustomUser(AbstractUser):
    """Кастомная модель юзера с добавлением аватара."""

    email = models.EmailField(
        'Почта',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH_NAME,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_NAME,
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True, blank=True,
        default=None,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='follower', verbose_name='Пользователь',
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following', verbose_name='Подписки',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'following'],
                                    name='unique_follow'),
            models.CheckConstraint(check=~models.Q(user=models.F('following')),
                                   name='prevent-sel-following'),
        ]

    def __str__(self):
        return f'Подписка {self.user.username} на {self.following.username}'
