from django import forms
from django.contrib.auth import authenticate, password_validation
from django.utils import timezone

from .models import User
from .throttle import client_ip, clear, is_locked, record_failure


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="At least 10 characters. Avoid common passwords.",
    )
    consent = forms.BooleanField(
        label="I agree to the privacy notice. Fuatilia stores the documents I upload so I can build my cases.",
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "phone"]
        labels = {"full_name": "Your full name", "phone": "Phone (optional)"}
        widgets = {"email": forms.EmailInput(attrs={"autocomplete": "email"})}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Sign in instead.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        if password:
            candidate = User(email=cleaned.get("email", ""), full_name=cleaned.get("full_name", ""))
            password_validation.validate_password(password, candidate)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.consented_at = timezone.now()
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").lower()
        password = cleaned.get("password")
        if not email or not password:
            return cleaned
        ip = client_ip(self.request)
        if is_locked(email, ip):
            raise forms.ValidationError("Too many failed attempts. Wait 15 minutes or reset your password.")
        user = authenticate(self.request, email=email, password=password)
        if user is None:
            record_failure(email, ip)
            raise forms.ValidationError("Email or password is incorrect.")
        clear(email)
        self.user = user
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "phone", "email_reminders"]
        labels = {"email_reminders": "Email me when a follow-up is due"}


class DeleteAccountForm(forms.Form):
    confirm = forms.CharField(
        label='Type DELETE to permanently remove your account, cases and documents',
    )

    def clean_confirm(self):
        if self.cleaned_data["confirm"].strip() != "DELETE":
            raise forms.ValidationError("Type DELETE in capital letters to confirm.")
        return self.cleaned_data["confirm"]
