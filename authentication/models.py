from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
import string

"""
Code taken from tutorial at https://thinkster.io/django-angularjs-tutorial
"""

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        customuser = self.model(
            email=self.normalize_email(email), username=kwargs.get('username')
        )

        customuser.set_password(password)
        customuser.key = self.make_random_password(32,
                string.digits+string.ascii_letters+string.punctuation)
        customuser.save()

        return customuser

    def create_superuser(self, email, password, **kwargs):
        customuser = self.create_user(email, password, **kwargs)

        customuser.is_admin = True
        customuser.save()

        return customuser

    def make_random_password(self, length=8,
        allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        """
        Generates a random password with the given length and given
        allowed_chars. Note that the default value of allowed_chars does not
        have "I" or "O" or letters and digits that look similar -- just to
        avoid confusion.
        """
        return get_random_string(length, allowed_chars)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)

    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=32, default='')
    word_count = models.TextField(default='{}')
    top_100_words = models.TextField(default='{}')
    pages_day = models.TextField(default='{}')
    pages_week = models.TextField(default='{}')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


@receiver(post_save, sender=CustomUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
