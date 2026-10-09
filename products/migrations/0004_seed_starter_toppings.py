from django.db import migrations


def seed_toppings(apps, schema_editor):
    Topping = apps.get_model("products", "Topping")
    sample_toppings = [
        # Drinks
        {"name": "Boba / Tapioca Pearls", "price": "0.50", "stock_quantity": 100, "applicable_category": "Drink"},
        {"name": "Egg Pudding", "price": "0.75", "stock_quantity": 80, "applicable_category": "Drink"},
        {"name": "Cheese Foam", "price": "0.80", "stock_quantity": 60, "applicable_category": "Drink"},
        {"name": "Extra Espresso Shot", "price": "0.75", "stock_quantity": 120, "applicable_category": "Drink"},
        {"name": "Oat Milk Swap", "price": "0.60", "stock_quantity": 90, "applicable_category": "Drink"},
        {"name": "Grass Jelly", "price": "0.50", "stock_quantity": 70, "applicable_category": "Drink"},
        # Food
        {"name": "Extra Melted Cheese", "price": "1.00", "stock_quantity": 100, "applicable_category": "Food"},
        {"name": "Crispy Bacon Strip", "price": "1.25", "stock_quantity": 80, "applicable_category": "Food"},
        {"name": "Truffle Mayo Dip", "price": "0.75", "stock_quantity": 50, "applicable_category": "Food"},
        {"name": "Caramelized Onions", "price": "0.50", "stock_quantity": 60, "applicable_category": "Food"},
    ]
    for top in sample_toppings:
        Topping.objects.get_or_create(
            name=top["name"],
            defaults={
                "price": top["price"],
                "stock_quantity": top["stock_quantity"],
                "applicable_category": top["applicable_category"],
                "is_active": True,
            },
        )


def unseed_toppings(apps, schema_editor):
    Topping = apps.get_model("products", "Topping")
    Topping.objects.filter(name__in=[
        "Boba / Tapioca Pearls", "Egg Pudding", "Cheese Foam", "Extra Espresso Shot",
        "Oat Milk Swap", "Grass Jelly", "Extra Melted Cheese", "Crispy Bacon Strip",
        "Truffle Mayo Dip", "Caramelized Onions"
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_topping"),
    ]

    operations = [
        migrations.RunPython(seed_toppings, unseed_toppings),
    ]
