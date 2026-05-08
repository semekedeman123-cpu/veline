from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    HomeView,
    PrivacyView,
    ProductsView,
    RemoveCartView,
    TermsView,
    UpdateCartView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("products/", ProductsView.as_view(), name="products"),
    path("cart/", CartView.as_view(), name="cart"),
    path("products/<slug:slug>/add/", AddToCartView.as_view(), name="cart-add"),
    path("products/<slug:slug>/update/", UpdateCartView.as_view(), name="cart-update"),
    path("products/<slug:slug>/remove/", RemoveCartView.as_view(), name="cart-remove"),
    path("privacy/", PrivacyView.as_view(), name="privacy"),
    path("terms/", TermsView.as_view(), name="terms"),
]
