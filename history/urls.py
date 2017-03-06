from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from history.views import (
    page_views, category_views, newpage_views, update_categories,
    close_tab, send_data, blacklist_views, session_views
    )

urlpatterns = [
    url(r'^pages/$', page_views.PageList.as_view()),
    url(r'^pages/(?P<id>[0-9]+)/$', page_views.PageDetail.as_view()),

    url(r'^categories/$', update_categories.SendCategories.as_view()),
    url(r'^checkcategories/$', update_categories.CheckPageCategories.as_view()),
    url(r'^activepage/$', update_categories.ActivePageCategories.as_view()),
    url(r'^addcategorypage/$', update_categories.AddCategoryPage.as_view()),
    url(r'^deletecategorypage/$', update_categories.DeleteCategoryPage.as_view()),
    url(r'^addcategory/$', update_categories.AddCategory.as_view()),
    url(r'^deletecategory/$', update_categories.DeleteCategory.as_view()),
    url(r'^editcategory/$', update_categories.EditCategory.as_view()),
    url(r'^updatestar/$', update_categories.UpdateStar.as_view()),

    url(r'^newpage/$', newpage_views.NewPage.as_view()),
    url(r'^active/$', newpage_views.UpdateActive.as_view()),

    url(r'^popupinfo/$', send_data.SendPopupInfo.as_view()),
    url(r'^tabinfo/$', send_data.SendTabs.as_view()),
    url(r'^domaininfo/$', send_data.SendDomain.as_view()),
    url(r'^getcategories/$', send_data.SendCategories.as_view()),
    url(r'^userinfo/$', send_data.SendUserData.as_view()),

    url(r'^closetab/$', close_tab.CloseTab.as_view()),
    url(r'^tabupdate/$', close_tab.TabUpdate.as_view()),

    url(r'^blacklists/$', blacklist_views.SendBlacklists.as_view()),
    url(r'^addblacklist/$', blacklist_views.CreateBlacklist.as_view()),
    url(r'^deleteblacklist/$', blacklist_views.DeleteBlacklist.as_view()),
    url(r'^editblacklist/$', blacklist_views.EditBlacklist.as_view()),

    url(r'^sessions/$', session_views.SendSessions.as_view()),
    url(r'^activesession/$', session_views.SendActiveSession.as_view()),
    url(r'^addsession/$', session_views.CreateSession.as_view()),
    url(r'^endsession/$', session_views.EndSession.as_view()),
    url(r'^deletesession/$', session_views.DeleteSession.as_view()),
    url(r'^editsession/$', session_views.EditSession.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
