from django.urls import path

from main.views import (
    CreateAccountApiView,
    LoginApiView,
    ProjectApiView,
    ProjectTaskApiView,
)

ACCOUNT_URLS = [
    # for creating account
    path("account/create/", CreateAccountApiView.as_view(), name="create-account"),


    # for login
    path("account/login/", LoginApiView.as_view(), name="login"),
]

urlpatterns = [
    path("project/", ProjectApiView.as_view(), name="project"),
    path("task/", ProjectTaskApiView.as_view(), name="task"),
    *ACCOUNT_URLS,
]
