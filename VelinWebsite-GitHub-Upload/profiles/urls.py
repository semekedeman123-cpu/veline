from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path
from django.views.generic import TemplateView

from .forms import LoginForm, PasswordResetRequestForm, StyledSetPasswordForm
from .views import (
    DashboardView,
    DeleteRequestView,
    ProfileExportView,
    ProfileUpdateView,
    PublicProfileView,
    PublishProfileView,
    ResendVerificationView,
    SignUpView,
    VerifyEmailView,
)

urlpatterns = [
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="auth/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path(
        "accounts/password-reset/",
        PasswordResetView.as_view(
            template_name="auth/password_reset_form.html",
            email_template_name="emails/password_reset.txt",
            subject_template_name="emails/password_reset_subject.txt",
            form_class=PasswordResetRequestForm,
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password-reset/done/",
        PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
            form_class=StyledSetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "verify-email/sent/",
        TemplateView.as_view(template_name="profiles/verification_sent.html"),
        name="verification-sent",
    ),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "verify-email/resend/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("dashboard/profile/", ProfileUpdateView.as_view(), name="profile-edit"),
    path("dashboard/profile/publish/", PublishProfileView.as_view(), name="profile-publish"),
    path("dashboard/profile/export/", ProfileExportView.as_view(), name="profile-export"),
    path(
        "dashboard/profile/delete-request/",
        DeleteRequestView.as_view(),
        name="delete-request",
    ),
    path("p/<str:public_id>/", PublicProfileView.as_view(), name="public-profile"),
]
