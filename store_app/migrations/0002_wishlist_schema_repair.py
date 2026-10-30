
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("store_app", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'DROP TABLE "store_app_wishlist"',
                        '''
                        CREATE TABLE "store_app_wishlist" (
                            "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            "added_at" datetime NOT NULL,
                            "user_id" INTEGER NOT NULL
                                REFERENCES "auth_user" ("id")
                                DEFERRABLE INITIALLY DEFERRED,
                            "product_id" INTEGER NOT NULL
                                REFERENCES "products_app_product" ("productID")
                                DEFERRABLE INITIALLY DEFERRED,
                            UNIQUE ("user_id", "product_id")
                        )
                        ''',
                        '''
                        CREATE INDEX "store_app_wishlist_user_idx"
                        ON "store_app_wishlist" ("user_id")
                        ''',
                        '''
                        CREATE INDEX "store_app_wishlist_product_idx"
                        ON "store_app_wishlist" ("product_id")
                        ''',
                    ],
                    reverse_sql=None,
                ),
            ],

            state_operations=[
                migrations.DeleteModel(name="WishlistItem"),

                migrations.RenameField(
                    model_name="wishlist",
                    old_name="created_at",
                    new_name="added_at",
                ),

                migrations.AlterField(
                    model_name="wishlist",
                    name="user",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist_items",
                        to="auth.user",
                    ),
                ),

                migrations.AddField(
                    model_name="wishlist",
                    name="product",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist_items",
                        to="products_app.product",
                    ),
                ),

                migrations.AlterUniqueTogether(
                    name="wishlist",
                    unique_together={("user", "product")},
                ),

                migrations.AlterModelOptions(
                    name="wishlist",
                    options={"ordering": ["-added_at"]},
                ),
            ],
        ),
    ]
