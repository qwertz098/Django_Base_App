import io
import base64

import qrcode
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django_otp.plugins.otp_totp.models import TOTPDevice

from .forms import LoginForm, ProfileForm, RegistrationForm, TOTPSetupForm, TOTPDisableForm

User = get_user_model()


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        # Check if user has a TOTP device
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if device:
            otp_token = form.cleaned_data.get("otp_token", "")
            if not otp_token or not device.verify_token(otp_token):
                from django.contrib.auth import logout
                logout(self.request)
                messages.error(self.request, "Invalid 2FA code.")
                return redirect("accounts:login")

        # Check if tenant requires 2FA and user doesn't have it
        from apps.tenants.models import TenantMembership
        memberships = TenantMembership.objects.filter(user=user).select_related("tenant")
        for membership in memberships:
            if membership.tenant.require_2fa and not device:
                messages.warning(
                    self.request,
                    f"Tenant '{membership.tenant.name}' requires 2FA. Please set it up.",
                )
                return redirect("accounts:totp_setup")

        return response


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("dashboard:home")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    totp_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    return render(request, "accounts/profile.html", {"form": form, "has_2fa": bool(totp_device)})


@login_required
def totp_setup(request):
    # Remove any unconfirmed devices
    TOTPDevice.objects.filter(user=request.user, confirmed=False).delete()

    device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    if device:
        messages.info(request, "2FA is already enabled.")
        return redirect("accounts:profile")

    # Create a new unconfirmed device
    device = TOTPDevice.objects.create(user=request.user, name="default", confirmed=False)

    if request.method == "POST":
        form = TOTPSetupForm(request.POST)
        if form.is_valid():
            if device.verify_token(form.cleaned_data["otp_token"]):
                device.confirmed = True
                device.save()
                messages.success(request, "2FA has been enabled.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Invalid code. Please try again.")
    else:
        form = TOTPSetupForm()

    # Generate QR code
    otpauth_url = device.config_url
    img = qrcode.make(otpauth_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_b64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "accounts/totp_setup.html", {
        "form": form,
        "qr_code": qr_code_b64,
        "secret_key": base64.b32encode(device.bin_key).decode(),
    })


@login_required
def totp_disable(request):
    device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
    if not device:
        messages.info(request, "2FA is not enabled.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = TOTPDisableForm(request.POST)
        if form.is_valid():
            if device.verify_token(form.cleaned_data["otp_token"]):
                device.delete()
                messages.success(request, "2FA has been disabled.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Invalid code.")
    else:
        form = TOTPDisableForm()

    return render(request, "accounts/totp_disable.html", {"form": form})
