from django import forms
from django.contrib.auth import get_user_model

from .models import Tenant, TenantMembership

User = get_user_model()


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ("name", "slug")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class TenantSettingsForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ("name", "require_2fa")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["require_2fa"].widget.attrs.update({"class": "form-check-input"})


class AddMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
    )
    role = forms.ChoiceField(
        choices=TenantMembership.Role.choices,
        initial=TenantMembership.Role.MEMBER,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f"User '{username}' does not exist.")
        if self.tenant and TenantMembership.objects.filter(tenant=self.tenant, user=user).exists():
            raise forms.ValidationError(f"User '{username}' is already a member of this tenant.")
        return username
