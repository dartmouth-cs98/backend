from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from history.views import page_views, category_views

urlpatterns = [
    url(r'^pages/$', page_views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', page_views.PageDetail.as_view()),
    url(r'^categories/$', category_views.CategoryList.as_view()),
    url(r'^categories/(?P<id>[0-9]+)/$', category_views.CategoryDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
