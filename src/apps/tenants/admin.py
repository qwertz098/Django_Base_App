from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Tenant, TenantMembership


def _get_admin_tenants(user):
    """Return tenant IDs where user is a tenant admin."""
    return TenantMembership.objects.filter(
        user=user, role=TenantMembership.Role.ADMIN
    ).values_list("tenant_id", flat=True)


class TenantMembershipInline(TabularInline):
    model = TenantMembership
    extra = 1
    autocomplete_fields = ["user"]


@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ("name", "slug", "is_active", "require_2fa", "created_at")
    list_filter = ("is_active", "require_2fa")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TenantMembershipInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id__in=_get_admin_tenants(request.user))

    def has_add_permission(self, request):
        # Only superusers can create tenants via admin
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(TenantMembership)
class TenantMembershipAdmin(ModelAdmin):
    list_display = ("user", "tenant", "role", "joined_at")
    list_filter = ("role", "tenant")
    search_fields = ("user__username", "user__email", "tenant__name")
    autocomplete_fields = ["user", "tenant"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(tenant_id__in=_get_admin_tenants(request.user))

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return _get_admin_tenants(request.user).exists()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return _get_admin_tenants(request.user).exists()
        return obj.tenant_id in _get_admin_tenants(request.user)
