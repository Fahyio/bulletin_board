from django.db import migrations, models
import django.db.models.deletion
import ads.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
                ('type', models.CharField(choices=[('sale', 'Продажа'), ('buy', 'Покупка')], default='sale', max_length=10, verbose_name='Тип')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('icon', models.CharField(blank=True, default='bi-tag', max_length=50, verbose_name='Иконка Bootstrap')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, validators=[ads.models.validate_title_length], verbose_name='Заголовок')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, validators=[ads.models.validate_price], verbose_name='Цена')),
                ('image', models.ImageField(blank=True, null=True, upload_to='ads/', verbose_name='Изображение')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='Город')),
                ('status', models.CharField(choices=[('active', 'Активно'), ('closed', 'Закрыто'), ('moderation', 'На модерации')], default='active', max_length=20, verbose_name='Статус')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                ('views_count', models.PositiveIntegerField(default=0, verbose_name='Просмотры')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='auth.user', verbose_name='Автор')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ads', to='ads.category', verbose_name='Категория')),
                ('tags', models.ManyToManyField(blank=True, related_name='ads', to='ads.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Объявление',
                'verbose_name_plural': 'Объявления',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000, verbose_name='Текст комментария')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='ads.ad', verbose_name='Объявление')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='auth.user', verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='auth.user', verbose_name='Пользователь')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='ads.ad', verbose_name='Объявление')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
                'unique_together': {('user', 'ad')},
                'ordering': ['-created_at'],
            },
        ),
    ]
