from django.db import models
from django.db.models import Q
from django.utils import timezone
from authentication.models import CustomUser
import math


class Category(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ('created',)

class Session(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50, default='No Title')
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class TimeActive(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('start',)

class Tab(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    tab_id = models.IntegerField()
    closed = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.tab_id)

    class Meta:
        ordering = ('created',)

class Domain(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    base_url = models.CharField(max_length=1000)
    favicon = models.TextField(blank=True, default='')
    tab = models.ForeignKey('Tab')
    closed = models.DateTimeField(blank=True, null=True)
    active_times = models.ManyToManyField(TimeActive, blank=True)
    opened_from_domain = models.ForeignKey('self', blank=True, null=True)
    opened_from_tabid = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def pagecount(self):
        return self.pagevisit_set.count()

    def timeactive(self, start=None, end=None):
        minutes_active = 0

        if start is None or end is None:
            ta = self.active_times.all()

            for a in ta:
                if a.end is not None:
                    time = a.end - a.start
                else:
                    time = timezone.now() - a.start
                minutes_active += math.ceil(time.seconds / 60)
        else:
            ta = self.active_times.filter(Q(start__range=[start, end]) |
                                          Q(end__range=[start, end]))

            for a in ta:
                if a.start < start:
                    time = a.end - start
                elif a.end is None or a.end > end:
                    time = end - a.start
                else:
                    time = a.end - a.start
                minutes_active += math.ceil(time.seconds / 60)

        return (minutes_active, ta)

    class Meta:
        ordering = ('created',)

class Page(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    url = models.CharField(max_length=1000)
    star = models.BooleanField(blank=True, default=False)
    blacklisted = models.BooleanField(blank=True, default=False)
    categories = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)

class PageVisit(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    visited = models.DateTimeField(auto_now_add=True)
    page = models.ForeignKey('Page')
    domain = models.ForeignKey('Domain')
    html = models.TextField(default='')
    session = models.ForeignKey('Session', blank=True, null=True)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'pagevisit'
        verbose_name_plural = 'pagevisits'
        ordering = ('visited',)

class Blacklist(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    created = models.DateTimeField(auto_now_add=True)
    base_url = models.CharField(max_length=1000)

    def __str__(self):
        return self.base_url
