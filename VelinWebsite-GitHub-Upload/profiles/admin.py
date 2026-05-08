from django.contrib import admin
from django.utils import timezone

from .models import ConsentRecord, DeletionRequest, Profile


@admin.action(description="Publish selected profiles")
def publish_profiles(modeladmin, request, queryset):
    for profile in queryset:
        if profile.email_verified:
            profile.is_published = True
            if not profile.published_at:
                profile.published_at = timezone.now()
            profile.save(update_fields=["is_published", "published_at", "updated_at"])


@admin.action(description="Unpublish selected profiles")
def unpublish_profiles(modeladmin, request, queryset):
    queryset.update(is_published=False)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "business_name",
        "public_id",
        "email_verified_at",
        "is_published",
        "updated_at",
    )
    list_filter = ("is_published", "email_verified_at")
    search_fields = ("full_name", "business_name", "user__email", "public_id")
    readonly_fields = ("public_id", "published_at", "created_at", "updated_at")
    actions = [publish_profiles, unpublish_profiles]


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "accepted", "version", "recorded_at")
    list_filter = ("kind", "accepted", "version")
    search_fields = ("user__email",)


@admin.register(DeletionRequest)
class DeletionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "requested_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("user__email", "reason")
