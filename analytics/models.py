from django.db import models
from authentication.models import CustomUser

class Day(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    date = models.DateField()
    weekday = models.IntegerField()
    pages = models.TextField(default='{}')
    domains = models.TextField(default='{}')
    categories = models.TextField(default='{}')

    def __str__(self):
        return str(self.date)

    class Meta:
        ordering = ('date',)
