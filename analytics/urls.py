from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from analytics.views import SendAnalytics

urlpatterns = [
    url(r'^analytics/$', SendAnalytics.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
