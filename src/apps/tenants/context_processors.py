from .models import TenantMembership


def tenant_context(request):
    """Add tenant-related context to all templates."""
    context = {
        "active_tenant": getattr(request, "tenant", None),
        "active_membership": getattr(request, "tenant_membership", None),
        "user_tenants": [],
    }

    if request.user.is_authenticated:
        context["user_tenants"] = (
            TenantMembership.objects.filter(user=request.user, tenant__is_active=True)
            .select_related("tenant")
            .order_by("tenant__name")
        )

    return context
