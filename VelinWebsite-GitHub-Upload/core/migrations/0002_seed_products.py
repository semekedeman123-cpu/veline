from decimal import Decimal

from django.db import migrations


def seed_products(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    products = [
        {
            "name": "Velin Card",
            "slug": "velin-card",
            "category": "cards",
            "material_label": "Premium Plastic",
            "description": "Premium plastic NFC business card with instant tap-to-connect technology.",
            "price_amount": Decimal("10.00"),
            "currency_code": "EUR",
            "stock_quantity": 48,
            "availability_status": "in_stock",
            "static_asset": "images/velin-card-black.png",
            "static_feature_asset": "images/velin-card-black.png",
            "display_order": 1,
            "is_featured": True,
        },
        {
            "name": "Velin Wooden Card",
            "slug": "velin-wooden-card",
            "category": "cards",
            "material_label": "Wood",
            "description": "Eco-friendly wooden NFC business card with a warm premium finish.",
            "price_amount": Decimal("20.00"),
            "currency_code": "EUR",
            "stock_quantity": 21,
            "availability_status": "in_stock",
            "static_asset": "images/velin-card-wood.png",
            "static_feature_asset": "images/velin-card-wood.png",
            "display_order": 2,
            "is_featured": True,
        },
        {
            "name": "Velin Metal Card",
            "slug": "velin-metal-card",
            "category": "cards",
            "material_label": "Stainless Steel",
            "description": "Sleek metal finish, crafted to leave a sharper and longer-lasting first impression.",
            "price_amount": Decimal("15.00"),
            "currency_code": "EUR",
            "stock_quantity": 17,
            "availability_status": "in_stock",
            "static_asset": "images/velin-card-black.png",
            "static_feature_asset": "images/velin-card-black.png",
            "display_order": 3,
            "is_featured": True,
        },
        {
            "name": "Velin Custom Design",
            "slug": "velin-custom-design",
            "category": "other",
            "material_label": "Premium Plastic / Metal",
            "description": "Upload your own design and create a truly unique NFC card that still feels unmistakably Velin.",
            "price_amount": Decimal("25.00"),
            "currency_code": "EUR",
            "stock_quantity": 10,
            "availability_status": "in_stock",
            "static_asset": "images/velin-card-custom.png",
            "static_feature_asset": "images/velin-card-custom.png",
            "display_order": 4,
            "is_featured": True,
        },
        {
            "name": "Velin NFC Stand",
            "slug": "velin-nfc-stand",
            "category": "other",
            "material_label": "Acrylic",
            "description": "Desk-ready NFC stand with custom branding for offices, reception areas, and events.",
            "price_amount": Decimal("10.00"),
            "currency_code": "EUR",
            "stock_quantity": 14,
            "availability_status": "in_stock",
            "static_asset": "images/velin-nfc-stand.png",
            "static_feature_asset": "images/velin-nfc-stand.png",
            "display_order": 5,
            "is_featured": False,
        },
        {
            "name": "Velin NFC Ring",
            "slug": "velin-nfc-ring",
            "category": "rings",
            "material_label": "Ceramic",
            "description": "Elegant NFC ring concept for a future always-on sharing experience.",
            "price_amount": Decimal("0.00"),
            "currency_code": "EUR",
            "stock_quantity": 0,
            "availability_status": "coming_soon",
            "static_asset": "images/velin-logo-mark.png",
            "static_feature_asset": "images/velin-logo-mark.png",
            "display_order": 6,
            "is_featured": False,
        },
    ]
    for payload in products:
        Product.objects.update_or_create(slug=payload["slug"], defaults=payload)


def unseed_products(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    Product.objects.filter(
        slug__in=[
            "velin-card",
            "velin-wooden-card",
            "velin-metal-card",
            "velin-custom-design",
            "velin-nfc-stand",
            "velin-nfc-ring",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
