from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from history import views

urlpatterns = [
    url(r'^pages/$', views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', views.PageDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
