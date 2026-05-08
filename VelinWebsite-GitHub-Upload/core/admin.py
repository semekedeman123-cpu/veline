from django.contrib import admin

from .models import Product

admin.site.site_header = "Velin Administration Database"
admin.site.site_title = "Velin Administration Database"
admin.site.index_title = "Velin technical control"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price_amount",
        "stock_quantity",
        "availability_status",
        "is_featured",
        "display_order",
    )
    list_filter = ("category", "availability_status", "is_featured")
    search_fields = ("name", "slug", "material_label", "description")
    ordering = ("display_order", "name")
    prepopulated_fields = {"slug": ("name",)}
