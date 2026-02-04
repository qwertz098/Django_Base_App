from django.conf import settings
from django.db import models


class Tenant(models.Model):
    """A tenant represents an organization/workspace that users can belong to."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    require_2fa = models.BooleanField(
        default=False,
        help_text="If enabled, all members must have 2FA configured to access this tenant.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TenantMembership(models.Model):
    """Links users to tenants with a role."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "user")
        ordering = ["tenant__name"]

    def __str__(self):
        return f"{self.user} - {self.tenant} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
