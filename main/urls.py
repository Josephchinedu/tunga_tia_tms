from django.urls import path

from main.views import (
    CreateAccountApiView,
    LoginApiView,
    ProjectApiView,
    ProjectTaskApiView,
)

ACCOUNT_URLS = [
    path("account/create/", CreateAccountApiView.as_view(), name="create-account"),
    path("account/login/", LoginApiView.as_view(), name="login"),
]

urlpatterns = [
    path("project/", ProjectApiView.as_view(), name="project"),
    path("task/", ProjectTaskApiView.as_view(), name="task"),
    *ACCOUNT_URLS,
]
