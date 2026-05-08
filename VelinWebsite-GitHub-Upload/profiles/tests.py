from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .services import make_verification_token

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SITE_URL="http://testserver",
)
class ProfileFlowTests(TestCase):
    def test_signup_creates_profile_and_sends_verification_email(self):
        response = self.client.post(
            reverse("signup"),
            {
                "full_name": "Elam Aamir",
                "email": "elam@example.com",
                "password1": "VelinStrongPass123!",
                "password2": "VelinStrongPass123!",
                "accept_privacy": True,
                "accept_terms": True,
                "marketing_consent": True,
            },
        )

        self.assertRedirects(response, reverse("verification-sent"))
        user = User.objects.get(email="elam@example.com")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.full_name, "Elam Aamir")
        self.assertEqual(user.consent_records.count(), 3)
        self.assertEqual(mail.outbox[0].to, ["elam@example.com"])

    def test_profile_cannot_publish_until_email_is_verified(self):
        user = User.objects.create_user(
            username="elam",
            email="elam@example.com",
            password="VelinStrongPass123!",
        )
        self.client.post(
            reverse("login"),
            {"username": "elam@example.com", "password": "VelinStrongPass123!"},
        )

        self.client.post(reverse("profile-publish"))

        user.profile.refresh_from_db()
        self.assertFalse(user.profile.is_published)

    def test_verified_profile_publishes_and_public_link_stays_stable(self):
        user = User.objects.create_user(
            username="elam",
            email="elam@example.com",
            password="VelinStrongPass123!",
        )
        public_id = user.profile.public_id

        token = make_verification_token(user)
        self.client.get(reverse("verify-email", args=[token]))
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verified)

        self.client.post(
            reverse("login"),
            {"username": "elam@example.com", "password": "VelinStrongPass123!"},
        )
        self.client.post(reverse("profile-publish"))
        user.profile.refresh_from_db()

        self.assertTrue(user.profile.is_published)
        self.assertEqual(user.profile.public_id, public_id)

        response = self.client.get(reverse("public-profile", args=[public_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "One Tap, Endless Connections")

    def test_dashboard_uses_profile_name_instead_of_raw_email_header(self):
        user = User.objects.create_user(
            username="elam",
            email="elam@example.com",
            password="VelinStrongPass123!",
        )
        user.profile.full_name = "Elam Aamir"
        user.profile.save(update_fields=["full_name", "updated_at"])

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Elam Aamir")

    @override_settings(GOOGLE_AUTH_ENABLED=True)
    def test_google_sign_in_button_can_be_exposed(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Continue with Google")

    def test_export_requires_login(self):
        response = self.client.get(reverse("profile-export"))
        self.assertEqual(response.status_code, 302)

    def test_changing_email_resets_verification_and_unpublishes_profile(self):
        user = User.objects.create_user(
            username="elam",
            email="elam@example.com",
            password="VelinStrongPass123!",
        )
        user.profile.email_verified_at = user.date_joined
        user.profile.is_published = True
        user.profile.save(update_fields=["email_verified_at", "is_published", "updated_at"])

        self.client.force_login(user)
        response = self.client.post(
            reverse("profile-edit"),
            {
                "full_name": user.profile.full_name,
                "email": "new@example.com",
                "business_name": "",
                "position_title": "",
                "phone_number": "",
                "bio": "",
                "website_url": "",
                "twitter_url": "",
                "instagram_url": "",
                "facebook_url": "",
                "linkedin_url": "",
                "youtube_url": "",
                "tiktok_url": "",
            },
        )

        self.assertRedirects(response, reverse("profile-edit"))
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")
        self.assertFalse(user.profile.email_verified)
        self.assertFalse(user.profile.is_published)
