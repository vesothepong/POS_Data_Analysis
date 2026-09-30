import random
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product
from sales.models import SalesRecord


class Command(BaseCommand):
    help = "Create demo products and 18 months of sales history (deterministic), plus a demo admin if no user exists."

    def handle(self, *args, **kwargs):
        rng = random.Random(42)
        # name, category, price, stock, reorder level, base monthly units
        products = [
            ("Artisan Cappuccino", "Beverages", 4.50, 180, 60, 160, "products/cappuccino.png", (53, 34, 23), (217, 119, 6), "Artisan Espresso & Foam"),
            ("Iced Matcha Latte", "Beverages", 5.25, 140, 45, 135, "products/matcha_latte.png", (20, 48, 30), (34, 197, 94), "Ceremonial Japanese Green Tea"),
            ("Fresh Orange Juice", "Beverages", 3.75, 90, 35, 95, "products/orange_juice.png", (67, 34, 12), (249, 115, 22), "100% Cold Pressed Citrus"),
            ("Sparkling Berry Soda", "Beverages", 2.95, 220, 50, 110, "products/berry_soda.png", (46, 16, 42), (236, 72, 153), "Sparkling Wild Berry Fizz"),
            ("Butter Croissant", "Food", 3.50, 75, 40, 140, "products/croissant.png", (58, 41, 19), (234, 179, 8), "Golden Flaky French Pastry"),
            ("Classic Cheeseburger", "Food", 8.95, 65, 30, 85, "products/cheeseburger.png", (60, 26, 20), (239, 68, 68), "Prime Beef & Melted Cheddar"),
            ("Chicken Caesar Wrap", "Food", 7.50, 50, 25, 70, "products/caesar_wrap.png", (27, 46, 32), (16, 185, 129), "Crispy Chicken & Caesar Greens"),
            ("Chocolate Lava Brownie", "Food", 4.25, 30, 35, 65, "products/brownie.png", (38, 24, 20), (168, 85, 247), "Warm Lava Fudge Brownie"),
        ]

        from django.conf import settings
        media_products = settings.MEDIA_ROOT / "products"
        media_products.mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image, ImageDraw
            for name, cat, price, stock, reorder, base, img_rel, bg, accent, subtitle in products:
                img_path = settings.BASE_DIR / "media" / img_rel
                if not img_path.exists():
                    img = Image.new('RGB', (600, 600), bg)
                    draw = ImageDraw.Draw(img)
                    for r in range(260, 0, -4):
                        glow_color = tuple(min(255, int(bg[i] + (accent[i] - bg[i]) * 0.5 * (1 - r/260))) for i in range(3))
                        draw.ellipse([300 - r, 230 - r, 300 + r, 230 + r], fill=glow_color)
                    draw.rounded_rectangle([25, 25, 575, 575], radius=28, outline=(255, 255, 255, 35), width=2)
                    draw.rounded_rectangle([230, 50, 370, 84], radius=17, fill=accent)
                    draw.text((300, 67), cat.upper(), fill=(255, 255, 255), anchor='mm', font_size=13)
                    draw.ellipse([175, 115, 425, 365], fill=(bg[0]//2, bg[1]//2, bg[2]//2), outline=accent, width=4)
                    draw.ellipse([190, 130, 410, 350], outline=(accent[0], accent[1], accent[2], 90), width=1)
                    draw.text((300, 235), name[0], fill=accent, anchor='mm', font_size=120)
                    draw.text((300, 425), name, fill=(255, 255, 255), anchor='mm', font_size=34)
                    draw.text((300, 470), subtitle, fill=(205, 215, 228), anchor='mm', font_size=17)
                    tag_text = 'FRESH DRINK' if cat == 'Beverages' else 'GOURMET FOOD'
                    draw.rounded_rectangle([210, 510, 390, 545], radius=16, fill=(255, 255, 255, 20), outline=(255, 255, 255, 40), width=1)
                    draw.text((300, 527), tag_text, fill=accent, anchor='mm', font_size=12)
                    img.save(img_path, 'PNG', quality=95)
        except Exception:
            pass

        old_apparel = ["T-Shirt", "Jeans", "Shoes", "Jacket", "Backpack", "Cap"]
        from shop.models import OrderItem
        from forecasting.models import Forecast
        with transaction.atomic():
            OrderItem.objects.filter(product__name__in=old_apparel).delete()
            Forecast.objects.filter(product__name__in=old_apparel).delete()
            Product.objects.filter(name__in=old_apparel).delete()
            for name, cat, price, stock, reorder, base, img_rel, *rest in products:
                p, _ = Product.objects.update_or_create(
                    name=name,
                    defaults={"category": cat, "price": Decimal(str(price)), "stock_quantity": stock, "reorder_level": reorder, "image": img_rel}
                )
                SalesRecord.objects.filter(product=p).delete()
                SalesRecord.objects.bulk_create([
                    SalesRecord(product=p, sale_date=date(2025 + m // 12, m % 12 + 1, 1),
                                quantity_sold=(q := max(10, base + m * 4 + rng.randint(-12, 12))),
                                price=Decimal(str(price)), total_amount=Decimal(str(q * price)), source_file="seed_demo")
                    for m in range(18)
                ])
            User = get_user_model()
            if not User.objects.exists():
                User.objects.create_superuser("admin", "admin@example.com", "admin12345")
                self.stdout.write(self.style.WARNING("Created demo admin     ->  username: admin     password: admin12345  (change it!)"))
            if not User.objects.filter(username="customer").exists():
                User.objects.create_user("customer", "customer@example.com", "customer12345")
                self.stdout.write(self.style.WARNING("Created demo customer  ->  username: customer  password: customer12345"))
        self.stdout.write(self.style.SUCCESS("Demo data created. Open Demand Forecast and choose 'All products'."))
