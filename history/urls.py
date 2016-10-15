from django.conf.urls import url
from history import views

urlpatterns = [
    url(r'^pages/$', views.page_list),
    url(r'^pages/(?P<id>[0-9]+)/$', views.page_detail),
]
