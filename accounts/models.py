from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from datetime import timedelta
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=40, blank=True, null=True)
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    address = models.TextField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'full_name']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin


class OTPCode(models.Model):
    code = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f'{self.code} for {self.phone_number}'

    def save(self, *args, **kwargs):
        self.expiry_time = timezone.localtime(timezone.now()) + timedelta(minutes=2)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.localtime(timezone.now()) > self.expiry_time
