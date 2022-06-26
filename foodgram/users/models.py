from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinLengthValidator
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя основанная на AbstractUser."""
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[MinLengthValidator(5, message='Минимум 5 символов')]
    )
    email = models.EmailField('Email адрес', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=15)
    is_subscribed = models.ManyToManyField(
        to='self',
        verbose_name='Подписка',
        related_name='subscribers',
        symmetrical=False,
        blank=True,
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'


class Follow(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="prevent_self_following",
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.following}'
