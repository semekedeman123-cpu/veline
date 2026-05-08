import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


def generate_public_id():
    return "vln_" + secrets.token_urlsafe(9).replace("-", "").replace("_", "")[:12]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    public_id = models.CharField(
        max_length=24, unique=True, default=generate_public_id, editable=False
    )
    full_name = models.CharField(max_length=120, blank=True)
    business_name = models.CharField(max_length=120, blank=True)
    position_title = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to="profiles/photos/", blank=True)
    pitch_media = models.FileField(upload_to="profiles/pitches/", blank=True)
    website_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.full_name or self.user.email or self.user.username

    @property
    def email_verified(self):
        return bool(self.email_verified_at)

    @property
    def contact_email(self):
        return self.user.email

    @property
    def display_name(self):
        value = (self.full_name or "").strip()
        if value and "@" not in value:
            return value
        fallback = (
            self.user.get_full_name()
            or self.user.username.split("@", 1)[0]
            or self.business_name
            or "Your Name"
        )
        return fallback

    @property
    def social_links(self):
        links = [
            ("Website", self.website_url),
            ("Instagram", self.instagram_url),
            ("LinkedIn", self.linkedin_url),
            ("Twitter", self.twitter_url),
            ("TikTok", self.tiktok_url),
            ("YouTube", self.youtube_url),
            ("Facebook", self.facebook_url),
        ]
        return [(label, url) for label, url in links if url]

    def get_absolute_url(self):
        return reverse("public-profile", kwargs={"public_id": self.public_id})

    def clean(self):
        if self.is_published and not self.email_verified:
            raise ValidationError("Email verification is required before publishing.")

    def publish(self):
        if not self.email_verified:
            raise ValidationError("Verify your email before publishing your profile.")
        self.is_published = True
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at", "updated_at"])

    def unpublish(self):
        self.is_published = False
        self.save(update_fields=["is_published", "updated_at"])


class ConsentRecord(models.Model):
    PRIVACY = "privacy"
    TERMS = "terms"
    MARKETING = "marketing"
    CONSENT_CHOICES = [
        (PRIVACY, "Privacy Policy"),
        (TERMS, "Terms of Service"),
        (MARKETING, "Marketing"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consent_records"
    )
    kind = models.CharField(max_length=20, choices=CONSENT_CHOICES)
    version = models.CharField(max_length=20, default="2026-04")
    accepted = models.BooleanField(default=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        state = "accepted" if self.accepted else "declined"
        return f"{self.user} · {self.kind} · {state}"


class DeletionRequest(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deletion_request"
    )
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Deletion request for {self.user}"
