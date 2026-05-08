from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .cart import add_to_cart, build_cart_summary, remove_cart_item, update_cart_item
from .models import Product

PUBLIC_HIDDEN_PRODUCT_SLUGS = {
    "velin-nfc-stand",
    "velin-nfc-ring",
}

DEFAULT_PRODUCTS = [
    {
        "name": "Velin Card",
        "slug": "velin-card",
        "category": Product.CATEGORY_CARDS,
        "material_label": "Premium Plastic",
        "description": "Premium plastic NFC business card with instant tap-to-connect technology.",
        "price_amount": Decimal("10.00"),
        "currency_code": "EUR",
        "stock_quantity": 48,
        "availability_status": Product.STATUS_IN_STOCK,
        "static_asset": "images/velin/black-plastic-velin-card.jpg",
        "static_feature_asset": "images/velin/black-plastic-velin-card.jpg",
        "display_order": 1,
        "is_featured": True,
    },
    {
        "name": "Velin Wooden Card",
        "slug": "velin-wooden-card",
        "category": Product.CATEGORY_CARDS,
        "material_label": "Wood",
        "description": "Eco-friendly wooden NFC business card with a warm premium finish.",
        "price_amount": Decimal("20.00"),
        "currency_code": "EUR",
        "stock_quantity": 21,
        "availability_status": Product.STATUS_IN_STOCK,
        "static_asset": "images/velin/wood-velin-card.jpg",
        "static_feature_asset": "images/velin/wood-velin-card.jpg",
        "display_order": 2,
        "is_featured": True,
    },
    {
        "name": "Velin Metal Card",
        "slug": "velin-metal-card",
        "category": Product.CATEGORY_CARDS,
        "material_label": "Stainless Steel",
        "description": "Sleek metal finish, crafted to leave a sharper and longer-lasting first impression.",
        "price_amount": Decimal("15.00"),
        "currency_code": "EUR",
        "stock_quantity": 17,
        "availability_status": Product.STATUS_IN_STOCK,
        "static_asset": "images/velin/metal-velin-card.jpg",
        "static_feature_asset": "images/velin/metal-velin-card.jpg",
        "display_order": 3,
        "is_featured": True,
    },
    {
        "name": "Velin Custom Design",
        "slug": "velin-custom-design",
        "category": Product.CATEGORY_OTHER,
        "material_label": "Premium Plastic / Metal",
        "description": "Upload your own design and create a truly unique NFC card that still feels unmistakably Velin.",
        "price_amount": Decimal("25.00"),
        "currency_code": "EUR",
        "stock_quantity": 10,
        "availability_status": Product.STATUS_IN_STOCK,
        "static_asset": "images/velin/live-extracted/velin-product-shot-custom-design.png",
        "static_feature_asset": "images/velin/live-extracted/velin-product-shot-custom-design.png",
        "display_order": 4,
        "is_featured": True,
    },
    {
        "name": "Velin NFC Stand",
        "slug": "velin-nfc-stand",
        "category": Product.CATEGORY_OTHER,
        "material_label": "Acrylic",
        "description": "Desk-ready NFC stand with custom branding for offices, reception areas, and events.",
        "price_amount": Decimal("10.00"),
        "currency_code": "EUR",
        "stock_quantity": 14,
        "availability_status": Product.STATUS_IN_STOCK,
        "static_asset": "images/velin/velin-nfc-stand.png",
        "static_feature_asset": "images/velin/velin-nfc-stand.png",
        "display_order": 5,
        "is_featured": False,
    },
    {
        "name": "Velin NFC Ring",
        "slug": "velin-nfc-ring",
        "category": Product.CATEGORY_RINGS,
        "material_label": "Ceramic",
        "description": "Elegant NFC ring concept for a future always-on sharing experience.",
        "price_amount": Decimal("0.00"),
        "currency_code": "EUR",
        "stock_quantity": 0,
        "availability_status": Product.STATUS_COMING_SOON,
        "static_asset": "",
        "static_feature_asset": "",
        "display_order": 6,
        "is_featured": False,
    },
]


def featured_fallback_products():
    return [product for product in all_fallback_products() if product["is_featured"]]


def all_fallback_products():
    return [
        product
        for product in DEFAULT_PRODUCTS
        if product["slug"] not in PUBLIC_HIDDEN_PRODUCT_SLUGS
    ]


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = list(
            Product.objects.exclude(slug__in=PUBLIC_HIDDEN_PRODUCT_SLUGS).order_by(
                "display_order", "name"
            )
        )
        featured = [product for product in products if product.is_featured] or products[:4]
        context["featured_products"] = featured or featured_fallback_products()
        context["why_choose"] = [
            {
                "title": "Premium first impressions",
                "copy": "Velin cards are designed to feel refined in hand, helping every introduction land with more confidence and polish.",
            },
            {
                "title": "One profile that stays current",
                "copy": "Keep one digital destination for your details, links, and identity, then update it anytime without replacing the card.",
            },
            {
                "title": "Built for modern teams",
                "copy": "From founders to sales teams, Velin supports a consistent brand presentation across meetings, events, and daily networking.",
            },
        ]
        context["how_it_works"] = [
            {
                "step": "01",
                "title": "Choose your Velin product",
                "copy": "Pick the finish that fits your brand, from matte black to wood or metal.",
            },
            {
                "step": "02",
                "title": "Create your digital profile",
                "copy": "Build one polished destination for your links, contact details, and professional presence.",
            },
            {
                "step": "03",
                "title": "Tap to share instantly",
                "copy": "Let people open your profile on the spot with a simple NFC tap from your card.",
            },
            {
                "step": "04",
                "title": "Update your profile anytime",
                "copy": "Refresh your details whenever things change without replacing the card in your pocket.",
            },
        ]
        return context


class ProductsView(TemplateView):
    template_name = "core/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_category = self.request.GET.get("category", "all")
        products = list(
            Product.objects.exclude(slug__in=PUBLIC_HIDDEN_PRODUCT_SLUGS).order_by(
                "display_order", "name"
            )
        )
        fallback_products = all_fallback_products()
        source_products = products or fallback_products
        if active_category != "all":
            source_products = [
                product
                for product in source_products
                if product.category == active_category
            ]
        context["products"] = source_products
        context["all_products"] = products or fallback_products
        context["active_category"] = active_category
        context["spotlight_product"] = source_products[0] if source_products else None
        context["category_options"] = [
            ("all", "All"),
            (Product.CATEGORY_CARDS, "Cards"),
            (Product.CATEGORY_OTHER, "Other"),
        ]
        return context


class CartView(TemplateView):
    template_name = "core/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_cart_summary(self.request))
        return context


class AddToCartView(View):
    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        if not product.can_purchase:
            messages.error(request, f"{product.name} is not available for purchase right now.")
            return redirect(request.POST.get("next") or "products")
        quantity = int(request.POST.get("quantity", 1) or 1)
        add_to_cart(request, product, quantity=quantity)
        messages.success(request, f"{product.name} added to your cart.")
        return redirect(request.POST.get("next") or "cart")


class UpdateCartView(View):
    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        quantity = int(request.POST.get("quantity", 1) or 1)
        update_cart_item(request, product, quantity)
        if quantity <= 0:
            messages.success(request, f"{product.name} removed from your cart.")
        else:
            messages.success(request, f"{product.name} quantity updated.")
        return redirect("cart")


class RemoveCartView(View):
    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        remove_cart_item(request, product.id)
        messages.success(request, f"{product.name} removed from your cart.")
        return redirect("cart")


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"


class TermsView(TemplateView):
    template_name = "core/terms.html"
