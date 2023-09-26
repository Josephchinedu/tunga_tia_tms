from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="TASK MANAGEMENT SYSTEM API",
        default_version="v1",
        description="TIA TASK MANAGEMENT SYSTEM API",
        terms_of_service="#",
        contact=openapi.Contact(email="developers@tunga.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(
        "redoc/", schema_view.with_ui("redoc", cache_timeout=500), name="schema-redoc"
    ),
    path("api/", include("main.urls")),
]
