from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            try:
                return self.image.url
            except Exception:
                return None
        return None

    def get_available_toppings(self):
        """Returns active toppings that apply to this product:
        either explicitly assigned, or matching this product's category, or globally available."""
        from django.db.models import Q
        return Topping.objects.filter(is_active=True).filter(
            Q(products=self) |
            (Q(products__isnull=True) & (Q(applicable_category="") | Q(applicable_category__iexact=self.category)))
        ).distinct()


class Topping(models.Model):
    name = models.CharField(max_length=120, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    applicable_category = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Category name this applies to (e.g. Drink, Beverage). Leave empty if globally available.",
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="toppings",
        help_text="Specific products this topping applies to (leave empty to apply by category or globally).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (+${self.price:.2f})"
