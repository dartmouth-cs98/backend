from django.contrib import admin
from .models import *


class DomainAdmin(admin.ModelAdmin):
	list_display = ['title', 'created', 'closed', 'tab']
	ordering = ['-created']

admin.site.register(Domain, DomainAdmin)
admin.site.register(Tab)
admin.site.register(Page)
admin.site.register(PageVisit)
