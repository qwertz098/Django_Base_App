from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.tenants.models import TenantMembership


@login_required
def home(request):
    """Dashboard home - aggregated view across all user's tenants."""
    memberships = (
        TenantMembership.objects.filter(user=request.user, tenant__is_active=True)
        .select_related("tenant")
        .order_by("tenant__name")
    )
    return render(request, "dashboard/home.html", {"memberships": memberships})
