from django.db import models
from authentication.models import CustomUser

class Day(models.Model):
    owned_by = models.ForeignKey('authentication.CustomUser', default=None)
    date = models.DateField()
    weekday = models.IntegerField()
    pages = models.TextField(default='{}')
    domains = models.TextField(default='{}')
    procrastination_visits = models.IntegerField(default=0)
    productivity_mins = models.IntegerField(default=0)
    procrastination_mins = models.IntegerField(default=0)
    categories = models.TextField(default='{}')

    def __str__(self):
        return str(self.date)

    class Meta:
        ordering = ('date',)
