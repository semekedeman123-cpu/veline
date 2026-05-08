from django.db import migrations


def refresh_product_assets(apps, schema_editor):
    Product = apps.get_model("core", "Product")

    asset_map = {
        "velin-card": "images/velin/black-plastic-velin-card.jpg",
        "velin-wooden-card": "images/velin/wood-velin-card.jpg",
        "velin-metal-card": "images/velin/metal-velin-card.jpg",
        "velin-custom-design": "images/velin/live-extracted/velin-product-shot-custom-design.png",
        "velin-nfc-stand": "images/velin/velin-nfc-stand.png",
        "velin-nfc-ring": "",
    }

    for slug, asset_path in asset_map.items():
        Product.objects.filter(slug=slug).update(
            static_asset=asset_path,
            static_feature_asset=asset_path,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_seed_products"),
    ]

    operations = [
        migrations.RunPython(refresh_product_assets, migrations.RunPython.noop),
    ]
