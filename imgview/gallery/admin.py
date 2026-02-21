from django.contrib import admin

from .models import Category, ImageItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by")
    search_fields = ("name",)


@admin.register(ImageItem)
class ImageItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "category", "uploaded_at")
    list_filter = ("category",)
    search_fields = ("title", "created_by__username")
