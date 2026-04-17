from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse


def validate_price(value):
    if value < 0:
        raise ValidationError('Цена не может быть отрицательной')
    if value > 1_000_000_000:
        raise ValidationError('Цена не может превышать 1 миллиард')


def validate_title_length(value):
    if len(value.strip()) < 5:
        raise ValidationError('Заголовок должен содержать минимум 5 символов')


class Category(models.Model):
    """Категория объявления"""
    SALE = 'sale'
    BUY = 'buy'

    TYPE_CHOICES = [
        (SALE, 'Продажа'),
        (BUY, 'Покупка'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='URL'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=SALE,
        verbose_name='Тип'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='bi-tag',
        verbose_name='Иконка Bootstrap'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'

    def get_absolute_url(self):
        return reverse('ads:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Тег для объявления"""
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='URL'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ad(models.Model):
    """Объявление — связь N:1 с User и Category"""
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'
    STATUS_MODERATION = 'moderation'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Активно'),
        (STATUS_CLOSED, 'Закрыто'),
        (STATUS_MODERATION, 'На модерации'),
    ]

    title = models.CharField(
        max_length=200,
        validators=[validate_title_length],
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_price],
        verbose_name='Цена'
    )
    image = models.ImageField(
        upload_to='ads/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ads',
        verbose_name='Категория'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='ads',
        verbose_name='Теги'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Город'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Статус'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Просмотры'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.author.username}'

    def get_absolute_url(self):
        return reverse('ads:detail', kwargs={'pk': self.pk})

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class Comment(models.Model):
    """Комментарий к объявлению — связь N:1 с Ad и User"""
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Объявление'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий {self.author.username} к "{self.ad.title}"'

    def clean(self):
        if self.text and len(self.text.strip()) < 3:
            raise ValidationError('Комментарий слишком короткий')


class Favorite(models.Model):
    """Избранное — связь N:N между User и Ad"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Объявление'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['user', 'ad']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.ad.title}'
