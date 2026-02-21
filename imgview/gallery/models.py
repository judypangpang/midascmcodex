from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categories",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
        permissions = [
            ("can_manage_all_categories", "Can manage all categories"),
        ]

    def __str__(self):
        return self.name


class ImageItem(models.Model):
    title = models.CharField(max_length=120)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    image = models.ImageField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("can_manage_all_images", "Can manage all images"),
        ]

    def __str__(self):
        return self.title
