import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView, UpdateView

from .forms import DeleteRequestForm, ProfileForm, SignUpForm
from .models import ConsentRecord, DeletionRequest, Profile
from .services import get_user_for_token, mark_email_verified, send_verification_email


class SignUpView(FormView):
    template_name = "auth/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("verification-sent")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        profile = user.profile
        profile.full_name = form.cleaned_data["full_name"]
        profile.save(update_fields=["full_name", "updated_at"])
        ConsentRecord.objects.bulk_create(
            [
                ConsentRecord(user=user, kind=ConsentRecord.PRIVACY, accepted=True),
                ConsentRecord(user=user, kind=ConsentRecord.TERMS, accepted=True),
                ConsentRecord(
                    user=user,
                    kind=ConsentRecord.MARKETING,
                    accepted=form.cleaned_data["marketing_consent"],
                ),
            ]
        )
        send_verification_email(user)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(
            self.request,
            "Your Velin account is ready. Check your inbox to verify your email before publishing.",
        )
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "profiles/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context["profile"] = profile
        context["public_url"] = self.request.build_absolute_uri(profile.get_absolute_url())
        context["deletion_request"] = getattr(self.request.user, "deletion_request", None)
        context["consents"] = self.request.user.consent_records.all()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "profiles/profile_form.html"
    model = Profile
    form_class = ProfileForm
    success_url = reverse_lazy("profile-edit")

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.email_changed:
            send_verification_email(self.request.user)
            messages.warning(
                self.request,
                "Your email changed, so verification was reset and the profile was returned to draft. Check your inbox for a fresh verification link.",
            )
        else:
            messages.success(self.request, "Your Velin profile has been saved.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context["profile"] = profile
        context["public_url"] = self.request.build_absolute_uri(profile.get_absolute_url())
        return context


class PublishProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        action = request.POST.get("action", "publish")
        if action == "unpublish":
            profile.unpublish()
            messages.success(request, "Your public Velin profile is now private again.")
            return redirect("dashboard")
        try:
            profile.publish()
        except ValidationError as exc:
            messages.error(request, exc.message)
        else:
            messages.success(
                request,
                "Your profile is live. Your Velin link is now ready to share.",
            )
        return redirect("dashboard")


class PublicProfileView(DetailView):
    template_name = "profiles/public_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        profile = get_object_or_404(Profile, public_id=self.kwargs["public_id"])
        if not profile.is_published:
            raise Http404("Profile not found.")
        return profile


class VerifyEmailView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            user = get_user_for_token(token)
        except Exception:
            messages.error(
                request,
                "That verification link is invalid or has expired. Request a fresh one from your dashboard.",
            )
            return redirect("dashboard" if request.user.is_authenticated else "login")
        mark_email_verified(user)
        messages.success(
            request,
            "Your email is verified. You can now publish your public Velin profile.",
        )
        return redirect("dashboard")


class ResendVerificationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        if profile.email_verified:
            messages.info(request, "Your email is already verified.")
        else:
            send_verification_email(request.user)
            messages.success(request, "A new verification email has been sent.")
        return redirect("dashboard")


class ProfileExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        payload = {
            "account": {
                "email": request.user.email,
                "date_joined": request.user.date_joined.isoformat(),
            },
            "profile": {
                "public_id": profile.public_id,
                "full_name": profile.full_name,
                "business_name": profile.business_name,
                "position_title": profile.position_title,
                "phone_number": profile.phone_number,
                "bio": profile.bio,
                "website_url": profile.website_url,
                "twitter_url": profile.twitter_url,
                "instagram_url": profile.instagram_url,
                "facebook_url": profile.facebook_url,
                "linkedin_url": profile.linkedin_url,
                "youtube_url": profile.youtube_url,
                "tiktok_url": profile.tiktok_url,
                "is_published": profile.is_published,
                "published_at": profile.published_at.isoformat() if profile.published_at else None,
                "email_verified_at": (
                    profile.email_verified_at.isoformat()
                    if profile.email_verified_at
                    else None
                ),
            },
            "consents": [
                {
                    "kind": consent.kind,
                    "accepted": consent.accepted,
                    "version": consent.version,
                    "recorded_at": consent.recorded_at.isoformat(),
                }
                for consent in request.user.consent_records.all()
            ],
        }
        response = HttpResponse(
            json.dumps(payload, indent=2), content_type="application/json"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="velin-profile-{profile.public_id}.json"'
        )
        return response


class DeleteRequestView(LoginRequiredMixin, FormView):
    template_name = "profiles/delete_request.html"
    form_class = DeleteRequestForm
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"], _ = DeletionRequest.objects.get_or_create(user=self.request.user)
        return kwargs

    def form_valid(self, form):
        deletion_request = form.save(commit=False)
        deletion_request.user = self.request.user
        deletion_request.status = DeletionRequest.STATUS_REQUESTED
        deletion_request.save()
        messages.success(
            self.request,
            "Your deletion request has been recorded. A staff member can now review it in the admin.",
        )
        return super().form_valid(form)
