from django.contrib import admin
from .models import Product, Category, ProductVariant

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('categoryID', 'name', 'description')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'productID',
        'name',
        'price',
        'category',
        'status'
    )

    list_filter = (
        'category',
        'status'
    )

    search_fields = (
        'name',
        'description'
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        'variantID',
        'product',
        'size',
        'color',
        'colorCode',
        'stockQuantity'
    )

    list_filter = (
        'size',
        'color'
    )

    search_fields = (
        'product__name',
    )