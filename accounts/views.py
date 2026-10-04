from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from cases.exports import build_account_export
from cases.models import Evidence

from .forms import DeleteAccountForm, LoginForm, ProfileForm, SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Welcome to Fuatilia. Start by opening your first case.")
        return redirect("case_new")
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        target = request.POST.get("next") or request.GET.get("next")
        if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(target)
        return redirect("dashboard")
    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def settings_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your details were saved.")
        return redirect("account_settings")
    return render(request, "accounts/settings.html", {"form": form, "delete_form": DeleteAccountForm()})


@login_required
def export_data(request):
    """Data subject access: everything we hold about the user, as a ZIP."""
    data = build_account_export(request.user)
    response = HttpResponse(data, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="fuatilia-my-data.zip"'
    return response


@login_required
@require_POST
def delete_account(request):
    form = DeleteAccountForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "accounts/settings.html",
            {"form": ProfileForm(instance=request.user), "delete_form": form},
            status=400,
        )
    user = request.user
    # Remove stored files first; database rows cascade when the user is deleted.
    for evidence in Evidence.objects.filter(case__owner=user).exclude(file=""):
        evidence.file.delete(save=False)
    logout(request)
    user.delete()
    messages.success(request, "Your account, cases and documents have been permanently deleted.")
    return redirect("home")
