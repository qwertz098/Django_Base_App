from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddMemberForm, TenantForm, TenantSettingsForm
from .models import Tenant, TenantMembership

User = get_user_model()


def _require_tenant_admin(request):
    """Return an error response if user is not a tenant admin, or None if OK."""
    if not request.tenant:
        messages.warning(request, "No active tenant.")
        return redirect("dashboard:home")
    if not request.tenant_membership or not request.tenant_membership.is_admin:
        return HttpResponseForbidden("You must be a tenant admin to access this page.")
    return None


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
    error = _require_tenant_admin(request)
    if error:
        return error

    if request.method == "POST":
        form = TenantSettingsForm(request.POST, instance=request.tenant)
        if form.is_valid():
            form.save()
            messages.success(request, "Tenant settings updated.")
            return redirect("tenants:settings")
    else:
        form = TenantSettingsForm(instance=request.tenant)

    members = TenantMembership.objects.filter(tenant=request.tenant).select_related("user")
    add_member_form = AddMemberForm(tenant=request.tenant)
    return render(request, "tenants/settings.html", {
        "form": form,
        "members": members,
        "add_member_form": add_member_form,
    })


@login_required
def add_member(request):
    """Add a user to the active tenant (admin only)."""
    error = _require_tenant_admin(request)
    if error:
        return error

    if request.method == "POST":
        form = AddMemberForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data["username"])
            TenantMembership.objects.create(
                tenant=request.tenant,
                user=user,
                role=form.cleaned_data["role"],
            )
            messages.success(request, f"Added {user.username} to {request.tenant.name}.")
        else:
            for field_errors in form.errors.values():
                for err in field_errors:
                    messages.error(request, err)

    return redirect("tenants:settings")


@login_required
def remove_member(request, membership_id):
    """Remove a user from the active tenant (admin only)."""
    error = _require_tenant_admin(request)
    if error:
        return error

    membership = get_object_or_404(TenantMembership, id=membership_id, tenant=request.tenant)

    if membership.user == request.user:
        messages.error(request, "You cannot remove yourself from the tenant.")
        return redirect("tenants:settings")

    username = membership.user.username
    membership.delete()
    messages.success(request, f"Removed {username} from {request.tenant.name}.")
    return redirect("tenants:settings")


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
