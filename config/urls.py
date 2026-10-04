from django.contrib import admin
from django.urls import include, path

from cases import views as case_views

urlpatterns = [
    path("", case_views.home, name="home"),
    path("privacy/", case_views.privacy, name="privacy"),
    path("health/", case_views.health, name="health"),
    path("accounts/", include("accounts.urls")),
    path("app/", include("cases.urls")),
    path("staff/", admin.site.urls),
]
