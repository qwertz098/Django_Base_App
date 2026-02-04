from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    path("switch/<int:tenant_id>/", views.switch_tenant, name="switch"),
    path("settings/", views.tenant_settings, name="settings"),
    path("members/add/", views.add_member, name="add_member"),
    path("members/<int:membership_id>/remove/", views.remove_member, name="remove_member"),
    path("create/", views.create_tenant, name="create"),
]
