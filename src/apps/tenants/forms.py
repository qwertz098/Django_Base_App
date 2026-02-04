from django import forms

from .models import Tenant


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
