from django.utils.deprecation import MiddlewareMixin

from .models import Tenant, TenantMembership


class ActiveTenantMiddleware(MiddlewareMixin):
    """
    Sets request.tenant to the currently active tenant for the user.
    The active tenant is stored in the session.
    """

    def process_request(self, request):
        request.tenant = None
        request.tenant_membership = None

        if not request.user.is_authenticated:
            return

        tenant_id = request.session.get("active_tenant_id")

        if tenant_id:
            try:
                membership = TenantMembership.objects.select_related("tenant").get(
                    tenant_id=tenant_id, user=request.user, tenant__is_active=True
                )
                request.tenant = membership.tenant
                request.tenant_membership = membership
                return
            except TenantMembership.DoesNotExist:
                # Stored tenant no longer valid, clear it
                del request.session["active_tenant_id"]

        # Auto-select first tenant if user has exactly one, or leave as None
        memberships = TenantMembership.objects.filter(
            user=request.user, tenant__is_active=True
        ).select_related("tenant")

        if memberships.count() == 1:
            membership = memberships.first()
            request.session["active_tenant_id"] = membership.tenant_id
            request.tenant = membership.tenant
            request.tenant_membership = membership
