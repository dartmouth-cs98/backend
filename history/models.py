from django.db import models


class Category(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)

class Tab(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tab_id = models.IntegerField()
    closed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.tab_id)

    class Meta:
        ordering = ('created',)

class Domain(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    base_url = models.CharField(max_length=1000)
    favicon = models.CharField(max_length=1000, blank=True, default='')
    tab = models.ForeignKey('Tab')
    closed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)

class Page(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=1000)
    star = models.BooleanField(blank=True, default=False)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)

class PageVisit(models.Model):
    visited = models.DateTimeField(auto_now_add=True)
    page = models.ForeignKey('Page')
    domain = models.ForeignKey('Domain')

    class Meta:
        ordering = ('visited',)
