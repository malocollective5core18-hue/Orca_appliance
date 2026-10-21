from django.contrib import admin
from django.urls import path

from config.health import healthz, readyz
from config.views import home

urlpatterns = [
    path("", home, name="home"),
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
    path("admin/", admin.site.urls),
]
