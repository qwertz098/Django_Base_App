from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Tenant, TenantMembership


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


@admin.register(TenantMembership)
class TenantMembershipAdmin(ModelAdmin):
    list_display = ("user", "tenant", "role", "joined_at")
    list_filter = ("role", "tenant")
    search_fields = ("user__username", "user__email", "tenant__name")
    autocomplete_fields = ["user", "tenant"]
