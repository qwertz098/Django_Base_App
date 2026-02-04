from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"})
    )
    otp_token = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "2FA Code (if enabled)"}),
        label="2FA Code",
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("username", "password1", "password2"):
            self.fields[field_name].widget.attrs.update(
                {"class": "form-control", "placeholder": self.fields[field_name].label}
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class TOTPSetupForm(forms.Form):
    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter 6-digit code"}),
        label="Verification Code",
    )


class TOTPDisableForm(forms.Form):
    otp_token = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter 6-digit code"}),
        label="Verification Code",
    )
