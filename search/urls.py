from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from search.views import Search

urlpatterns = [
    url(r'^search/$', Search.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
