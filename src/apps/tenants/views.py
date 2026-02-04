from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TenantForm, TenantSettingsForm
from .models import Tenant, TenantMembership


@login_required
def switch_tenant(request, tenant_id):
    """Switch the active tenant for the current user."""
    membership = get_object_or_404(
        TenantMembership, tenant_id=tenant_id, user=request.user, tenant__is_active=True
    )
    request.session["active_tenant_id"] = membership.tenant_id
    messages.success(request, f"Switched to {membership.tenant.name}.")
    return redirect("dashboard:home")


@login_required
def tenant_settings(request):
    """Tenant settings page (admin only)."""
    if not request.tenant:
        messages.warning(request, "No active tenant.")
        return redirect("dashboard:home")

    if not request.tenant_membership or not request.tenant_membership.is_admin:
        return HttpResponseForbidden("You must be a tenant admin to access settings.")

    if request.method == "POST":
        form = TenantSettingsForm(request.POST, instance=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, "Tenant settings updated.")
            return redirect("tenants:settings")
    else:
        form = TenantSettingsForm(instance=request.tenant)

    members = TenantMembership.objects.filter(tenant=request.tenant).select_related("user")
    return render(request, "tenants/settings.html", {"form": form, "members": members})


@login_required
def create_tenant(request):
    """Create a new tenant. The creating user becomes the admin."""
    if request.method == "POST":
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            TenantMembership.objects.create(
                tenant=tenant, user=request.user, role=TenantMembership.Role.ADMIN
            )
            request.session["active_tenant_id"] = tenant.id
            messages.success(request, f"Tenant '{tenant.name}' created.")
            return redirect("dashboard:home")
    else:
        form = TenantForm()
    return render(request, "tenants/create.html", {"form": form})
