from django.urls import path

from . import views

urlpatterns = [
    path("", views.image_list, name="image_list"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("upload/", views.image_upload, name="image_upload"),
    path("images/<int:pk>/edit/", views.image_update, name="image_update"),
    path("images/<int:pk>/delete/", views.image_delete, name="image_delete"),
    path("images/<int:pk>/category/", views.image_category_update, name="image_category_update"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("<int:pk>/", views.image_detail, name="image_detail"),
]
