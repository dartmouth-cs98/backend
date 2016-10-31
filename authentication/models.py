from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, get_random_string
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):


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
    token = models.CharField(max_length=128, default='', blank=True)

    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def generate_token(self):
        import uuid

        token = uuid.uuid4().hex

        while CustomUser.objects.filter(token=token).exists():
            token = uuid.uuid4().hex

        self.token = token
        self.save()
