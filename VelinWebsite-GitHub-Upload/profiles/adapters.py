from django.contrib.auth import get_user_model

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .forms import build_unique_username
from .models import ConsentRecord
from .services import mark_email_verified

User = get_user_model()


class VelinSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or "").strip().lower()
        if not email or sociallogin.is_existing:
            return
        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user:
            sociallogin.connect(request, existing_user)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = (data.get("email") or sociallogin.user.email or "").strip().lower()
        full_name = (
            data.get("name")
            or sociallogin.account.extra_data.get("name")
            or user.get_full_name()
            or email.split("@", 1)[0]
        )
        if email:
            user.email = email
        if not user.username:
            source_email = email or f"{full_name.replace(' ', '.')}@velin.local"
            user.username = build_unique_username(source_email)
        if full_name and not user.get_full_name():
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        profile = user.profile
        if not profile.full_name:
            profile.full_name = user.get_full_name() or user.email or user.username
            profile.save(update_fields=["full_name", "updated_at"])
        extra_data = sociallogin.account.extra_data
        if extra_data.get("email_verified") or extra_data.get("verified_email"):
            mark_email_verified(user)
        existing_kinds = set(user.consent_records.values_list("kind", flat=True))
        new_records = []
        for kind, accepted in [
            (ConsentRecord.PRIVACY, True),
            (ConsentRecord.TERMS, True),
            (ConsentRecord.MARKETING, False),
        ]:
            if kind not in existing_kinds:
                new_records.append(
                    ConsentRecord(user=user, kind=kind, accepted=accepted)
                )
        if new_records:
            ConsentRecord.objects.bulk_create(new_records)
        return user
