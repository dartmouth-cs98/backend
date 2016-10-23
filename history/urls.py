from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from history.views import page_views, category_views

urlpatterns = [
<<<<<<< HEAD
    url(r'^pages/$', views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', views.PageDetail.as_view()),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<id>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
=======
    url(r'^pages/$', page_views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', page_views.PageDetail.as_view()),
    url(r'^categories/$', category_views.CategoryList.as_view()),
    url(r'^categories/(?P<id>[0-9]+)/$', category_views.CategoryDetail.as_view()),
>>>>>>> 4cbeb61562478bfcf0c14ea4abb62b60472cf271
]


urlpatterns = format_suffix_patterns(urlpatterns)
