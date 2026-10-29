from django.contrib import admin

# Register your models here.
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'email', 'comment')