from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

ROLE = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(regex=r'^[\w.@+-]',
                           message='Недопустимые символы в имени пользователя')
        ]
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        'Роль',
        choices=ROLE,
        max_length=10,
        default='user',
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
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
