from django.contrib.auth.models import AbstractUser, Permission, Group
from django.core.validators import RegexValidator

from django.contrib.auth.models import BaseUserManager
from django.db import models
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    groups = models.ManyToManyField(Group, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions')
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    phone = models.CharField(
        max_length=15,
        verbose_name='Телефон',
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        blank=True,
        null=True,
        help_text="Введите номер телефона"
    )
    country = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    verification_token = models.CharField(max_length=100, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def generate_verification_token(self):
        "Генерация и сохранение токена верификации"
        self.verification_token = secrets.token_urlsafe(32)
        self.save()
        return self.verification_token

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
