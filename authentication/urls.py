from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from authentication.views import (
    CreateCustomUserView, LoginView, LogoutView,
    ForgotPassword, ChangePassword,
    ChangeTracking, GetDecryption
        )


urlpatterns = [
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^users/$', CreateCustomUserView.as_view()),
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^forgot/$', ForgotPassword.as_view()),
    url(r'^change/$', ChangePassword.as_view()),
    url(r'^tracking/$', ChangeTracking.as_view()),
    url(r'^decrypt/$', GetDecryption.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
