from django.db import models

# Create your models here.

class Category(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)

class Page(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    star = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)
