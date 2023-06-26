from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.global_constants import (
    USERNAME_LENGTH,
    EMAIL_LENGTH,
    FIRST_NAME_LENGTH,
    LAST_NAME_LENGTH,
    ROLE_LENGTH,
    PASSWORD_LENGTH,
)

ROLE = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
)


class User(AbstractUser):
    '''
    Кастомная модель пользователя.
    '''
    username = models.CharField(
        'Имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]',
                           message='Недопустимые символы в имени пользователя')
        ]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_LENGTH,
        blank=True,
    )
    role = models.CharField(
        'Роль',
        choices=ROLE,
        max_length=ROLE_LENGTH,
        default='user',
    )
    password = models.CharField(
        'Пароль',
        max_length=PASSWORD_LENGTH,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-date_joined', ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return self.role == User.ROLE[1][0]

    def __str__(self) -> str:
        return self.username


class Subscribe(models.Model):
    '''
    Модель реализации подписки на авторов рецептов.
    '''
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Подписчик автора рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
        help_text='Автор рецепта'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['author', 'subscriber'],
            name='unique_subscription'
        )]

    def __str__(self) -> str:
        return (f'Пользователь {self.subscriber.username}'
                f' подписан на {self.author.username}')
