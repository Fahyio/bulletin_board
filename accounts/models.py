from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


def validate_phone(value):
    pattern = r'^\+7\d{10}$'
    if value and not re.match(pattern, value):
        raise ValidationError(
            'Номер телефона должен быть в формате +7XXXXXXXXXX'
        )


def validate_avatar_size(image):
    max_size = 2 * 1024 * 1024  # 2MB
    if image.size > max_size:
        raise ValidationError('Размер изображения не должен превышать 2MB')


class UserProfile(models.Model):
    """Профиль пользователя — связь 1:1 с User"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    phone = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[validate_phone],
        verbose_name='Телефон'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[validate_avatar_size],
        verbose_name='Аватар'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        verbose_name='О себе'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Город'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_ads_count(self):
        return self.user.ads.count()
