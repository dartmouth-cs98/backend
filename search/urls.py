from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from search.views import Search, GetHTML

urlpatterns = [
    url(r'^search/$', Search.as_view()),
    url(r'^gethtml/$', GetHTML.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
