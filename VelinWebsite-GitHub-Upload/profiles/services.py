from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

EMAIL_VERIFICATION_SALT = "profiles.email-verification"


def make_verification_token(user):
    payload = {"user_id": user.pk, "email": user.email}
    return signing.dumps(payload, salt=EMAIL_VERIFICATION_SALT)


def get_user_for_token(token, max_age=60 * 60 * 48):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    payload = signing.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=max_age)
    return User.objects.get(pk=payload["user_id"], email=payload["email"])


def send_verification_email(user):
    token = make_verification_token(user)
    verification_url = (
        f"{settings.SITE_URL.rstrip('/')}"
        f"{reverse('verify-email', kwargs={'token': token})}"
    )
    message = render_to_string(
        "emails/verify_email.txt",
        {"user": user, "verification_url": verification_url},
    )
    send_mail(
        subject="Verify your Velin email",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def mark_email_verified(user):
    profile = user.profile
    if not profile.email_verified_at:
        profile.email_verified_at = timezone.now()
        profile.save(update_fields=["email_verified_at", "updated_at"])
