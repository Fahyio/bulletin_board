from django.db import migrations, models
import django.db.models.deletion
import accounts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=12, null=True, validators=[accounts.models.validate_phone], verbose_name='Телефон')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', validators=[accounts.models.validate_avatar_size], verbose_name='Аватар')),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='О себе')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Город')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
    ]
