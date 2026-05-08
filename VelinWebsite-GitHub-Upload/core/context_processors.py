from decimal import Decimal

from django.conf import settings


def global_context(request):
    cart = request.session.get("cart", {})
    cart_count = 0
    cart_total = Decimal("0.00")
    for item in cart.values():
        quantity = int(item.get("quantity", 0) or 0)
        cart_count += quantity
        try:
            cart_total += Decimal(str(item.get("subtotal", "0.00")))
        except Exception:
            continue

    display_name = ""
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        display_name = (
            (profile.display_name if profile else "")
            or request.user.get_full_name()
            or request.user.username
            or request.user.email
        )

    return {
        "google_auth_enabled": settings.GOOGLE_AUTH_ENABLED,
        "cart_count": cart_count,
        "cart_total": cart_total,
        "nav_display_name": display_name,
    }
