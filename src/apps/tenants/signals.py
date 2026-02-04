from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import TenantMembership


def _sync_staff_status(user):
    """
    Set is_staff=True if user is admin of any tenant, False otherwise.
    Superusers are never demoted.
    """
    if user.is_superuser:
        return
    is_tenant_admin = TenantMembership.objects.filter(
        user=user, role=TenantMembership.Role.ADMIN
    ).exists()
    if user.is_staff != is_tenant_admin:
        user.is_staff = is_tenant_admin
        user.save(update_fields=["is_staff"])


@receiver(post_save, sender=TenantMembership)
def membership_saved(sender, instance, **kwargs):
    _sync_staff_status(instance.user)


@receiver(post_delete, sender=TenantMembership)
def membership_deleted(sender, instance, **kwargs):
    _sync_staff_status(instance.user)
