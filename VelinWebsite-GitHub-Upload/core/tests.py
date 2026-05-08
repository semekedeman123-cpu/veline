from django.test import TestCase
from django.urls import reverse

from .models import Product


class HomeAndCommerceTests(TestCase):
    def test_home_page_loads_with_new_sections(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Why Choose Velin")
        self.assertContains(response, "Premium first impressions")
        self.assertContains(response, "Choose your Velin product")
        self.assertNotContains(response, "Hosted In Europe")

    def test_products_page_renders_seeded_catalog(self):
        response = self.client.get(reverse("products"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Velin Card")
        self.assertContains(response, "Velin Wooden Card")
        self.assertNotContains(response, "Velin NFC Ring")

    def test_cart_add_and_update_respect_stock(self):
        product = Product.objects.get(slug="velin-card")

        self.client.post(reverse("cart-add", args=[product.slug]), {"quantity": 2})
        session = self.client.session
        self.assertEqual(session["cart"][str(product.id)]["quantity"], 2)

        self.client.post(
            reverse("cart-update", args=[product.slug]),
            {"quantity": product.stock_quantity + 20},
        )
        session = self.client.session
        self.assertEqual(
            session["cart"][str(product.id)]["quantity"], product.stock_quantity
        )

    def test_coming_soon_product_cannot_be_added(self):
        product = Product.objects.get(slug="velin-nfc-ring")

        response = self.client.post(reverse("cart-add", args=[product.slug]))

        self.assertRedirects(response, reverse("products"))
        self.assertNotIn("cart", self.client.session)
