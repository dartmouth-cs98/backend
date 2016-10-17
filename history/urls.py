from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from history import views

urlpatterns = [
    url(r'^pages/$', views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', views.PageDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<id>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]


urlpatterns = format_suffix_patterns(urlpatterns)
