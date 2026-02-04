from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    path("switch/<int:tenant_id>/", views.switch_tenant, name="switch"),
    path("settings/", views.tenant_settings, name="settings"),
    path("create/", views.create_tenant, name="create"),
]
