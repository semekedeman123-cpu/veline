from django.db import models


class ShowcaseItem(models.Model):
    THEME_CHOICES = [
        ("ink", "Ink"),
        ("wood", "Wood"),
        ("glass", "Glass"),
    ]

    title = models.CharField(max_length=120)
    eyebrow = models.CharField(max_length=80, blank=True)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to="showcase/", blank=True)
    link_label = models.CharField(max_length=80, default="Create Profile")
    link_url = models.CharField(max_length=255, default="/accounts/signup/")
    theme = models.CharField(max_length=12, choices=THEME_CHOICES, default="ink")
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title


class Product(models.Model):
    CATEGORY_CARDS = "cards"
    CATEGORY_RINGS = "rings"
    CATEGORY_OTHER = "other"
    CATEGORY_CHOICES = [
        (CATEGORY_CARDS, "Cards"),
        (CATEGORY_RINGS, "Rings"),
        (CATEGORY_OTHER, "Other"),
    ]

    STATUS_IN_STOCK = "in_stock"
    STATUS_LOW_STOCK = "low_stock"
    STATUS_SOLD_OUT = "sold_out"
    STATUS_COMING_SOON = "coming_soon"
    STATUS_CHOICES = [
        (STATUS_IN_STOCK, "In stock"),
        (STATUS_LOW_STOCK, "Low stock"),
        (STATUS_SOLD_OUT, "Sold out"),
        (STATUS_COMING_SOON, "Coming soon"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_CARDS
    )
    material_label = models.CharField(max_length=80, blank=True)
    description = models.TextField()
    price_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="EUR")
    stock_quantity = models.PositiveIntegerField(default=0)
    availability_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_STOCK
    )
    primary_image = models.ImageField(upload_to="products/", blank=True)
    static_asset = models.CharField(max_length=255, blank=True)
    feature_media = models.FileField(upload_to="products/feature/", blank=True)
    static_feature_asset = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    @property
    def can_purchase(self):
        return self.availability_status in {
            self.STATUS_IN_STOCK,
            self.STATUS_LOW_STOCK,
        } and self.stock_quantity > 0

    @property
    def availability_label(self):
        return self.get_availability_status_display()

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category.title())
