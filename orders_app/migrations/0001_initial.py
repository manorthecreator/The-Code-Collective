from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("products_app", "0004_productimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=30)),
                ("delivery_address", models.TextField()),
                ("payment_method", models.CharField(choices=[("cash", "Cash on delivery"), ("card", "Card payment")], max_length=20)),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("AWAITING_PAYMENT", "Awaiting online payment"), ("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")], default="PENDING", max_length=30)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("delivery_fee", models.DecimalField(decimal_places=2, default=100, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=200)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="orders_app.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="products_app.product")),
            ],
        ),
    ]
