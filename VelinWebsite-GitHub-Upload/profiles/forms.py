from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.template.defaultfilters import slugify

from .models import DeletionRequest, Profile

User = get_user_model()


class StyledFormMixin:
    input_class = "form-input"
    checkbox_class = "form-checkbox"

    def apply_styling(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", self.checkbox_class)
                continue
            widget.attrs.setdefault("class", self.input_class)
            widget.attrs.setdefault("autocomplete", "off")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styling()


def build_unique_username(email):
    local_part = email.split("@", 1)[0]
    base = slugify(local_part) or "velin-user"
    candidate = base[:140]
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base[:130]}-{suffix}"
        suffix += 1
    return candidate


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"placeholder": "you@example.com"})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
    )

    def clean(self):
        email = self.cleaned_data.get("username", "").strip().lower()
        if email:
            user = User.objects.filter(email__iexact=email).first()
            if user:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()


class SignUpForm(StyledFormMixin, UserCreationForm):
    username = None
    full_name = forms.CharField(max_length=120, label="Full name")
    email = forms.EmailField(label="Email")
    accept_privacy = forms.BooleanField(
        label="I have read the Privacy Policy and agree to the processing of my data."
    )
    accept_terms = forms.BooleanField(
        label="I agree to the Terms of Service and understand Velin's publishing rules."
    )
    marketing_consent = forms.BooleanField(
        required=False,
        label="I'd like to receive optional product updates and launch news.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("full_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = build_unique_username(user.email)
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(StyledFormMixin, PasswordResetForm):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"placeholder": "you@example.com"})
    )


class StyledSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass


class ProfileForm(StyledFormMixin, forms.ModelForm):
    email = forms.EmailField(label="Email")

    class Meta:
        model = Profile
        fields = [
            "profile_photo",
            "full_name",
            "email",
            "business_name",
            "position_title",
            "phone_number",
            "bio",
            "website_url",
            "twitter_url",
            "instagram_url",
            "facebook_url",
            "linkedin_url",
            "youtube_url",
            "tiktok_url",
            "pitch_media",
        ]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Tell people who you are and why they should connect.",
                }
            ),
            "full_name": forms.TextInput(attrs={"placeholder": "Elam Aamir"}),
            "business_name": forms.TextInput(attrs={"placeholder": "Velin"}),
            "position_title": forms.TextInput(attrs={"placeholder": "Founder"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+420 ..."}),
            "website_url": forms.URLInput(attrs={"placeholder": "https://yourwebsite.com"}),
            "twitter_url": forms.URLInput(attrs={"placeholder": "https://twitter.com/..."}),
            "instagram_url": forms.URLInput(
                attrs={"placeholder": "https://instagram.com/..."}
            ),
            "facebook_url": forms.URLInput(
                attrs={"placeholder": "https://facebook.com/..."}
            ),
            "linkedin_url": forms.URLInput(
                attrs={"placeholder": "https://linkedin.com/in/..."}
            ),
            "youtube_url": forms.URLInput(
                attrs={"placeholder": "https://youtube.com/..."}
            ),
            "tiktok_url": forms.URLInput(attrs={"placeholder": "https://tiktok.com/..."}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.original_email = self.user.email
        self.email_changed = False
        self.fields["email"].initial = self.user.email
        self.fields["profile_photo"].widget.attrs["accept"] = "image/png,image/jpeg,image/gif"
        self.fields["pitch_media"].widget.attrs["accept"] = "audio/*,video/*"
        self.fields["profile_photo"].widget.attrs["class"] = "form-input file-input"
        self.fields["pitch_media"].widget.attrs["class"] = "form-input file-input"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("That email address is already in use.")
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile photos must be 5MB or smaller.")
        return photo

    def clean_pitch_media(self):
        media = self.cleaned_data.get("pitch_media")
        if media and media.size > 50 * 1024 * 1024:
            raise forms.ValidationError("Business pitch uploads must be 50MB or smaller.")
        allowed = {".mp3", ".mp4", ".wav", ".mov", ".m4a", ".webm"}
        if media and Path(media.name).suffix.lower() not in allowed:
            raise forms.ValidationError(
                "Upload an MP3, MP4, WAV, MOV, M4A, or WEBM file."
            )
        return media

    def save(self, commit=True):
        profile = super().save(commit=False)
        new_email = self.cleaned_data["email"]
        self.email_changed = new_email != self.original_email
        self.user.email = new_email
        if self.email_changed:
            profile.email_verified_at = None
            profile.is_published = False
        if commit:
            self.user.save(update_fields=["email"])
            profile.save()
        return profile


class DeleteRequestForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DeletionRequest
        fields = ["reason"]
        widgets = {
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us anything we should know before we remove your account and public profile.",
                }
            )
        }
