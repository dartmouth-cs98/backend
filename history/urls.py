from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from history.views import (
    page_views, category_views, newpage_views, update_categories,
    close_tab, send_data
    )

urlpatterns = [
    url(r'^pages/$', page_views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', page_views.PageDetail.as_view()),
    url(r'^categories/$', category_views.CategoryList.as_view()),
    url(r'^categories/(?P<id>[0-9]+)/$', category_views.CategoryDetail.as_view()),
    url(r'^newpage/$', newpage_views.NewPage.as_view()),
    url(r'^tabinfo/$', send_data.SendTabs.as_view()),
    url(r'^active/$', newpage_views.UpdateActive.as_view()),
    url(r'^checkcategories/$', update_categories.CheckPageCategories.as_view()),
    url(r'^addcategorypage/$', update_categories.AddCategoryPage.as_view()),
    url(r'^deletecategorypage/$', update_categories.DeleteCategoryPage.as_view()),
    url(r'^addcategory/$', update_categories.AddCategory.as_view()),
    url(r'^deletecategory/$', update_categories.DeleteCategory.as_view()),
    url(r'^updatestar/$', update_categories.UpdateStar.as_view()),
    url(r'^closetab/$', close_tab.CloseTab.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
