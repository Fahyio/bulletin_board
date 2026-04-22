from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Телефон должен быть в формате: +999999999. До 15 цифр."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username