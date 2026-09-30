from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("image_preview", "name", "category", "price", "stock_quantity", "reorder_level", "updated_at")
    list_filter = ("category",)
    search_fields = ("name", "category")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:36px;height:36px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;" />', obj.image.url)
        return format_html('<span style="color:#94a3b8;font-size:12px;">No image</span>')
    image_preview.short_description = "Image"
