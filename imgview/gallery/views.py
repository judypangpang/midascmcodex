from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CategoryForm, ImageCategoryUpdateForm, ImageItemForm, SignUpForm
from .models import Category, ImageItem


def _can_manage_all_categories(user):
    return user.has_perm("gallery.can_manage_all_categories")


def _can_manage_category(user, category):
    return _can_manage_all_categories(user) or category.created_by_id == user.id


def _can_manage_all_images(user):
    return user.has_perm("gallery.can_manage_all_images")


def _can_manage_image(user, image):
    return _can_manage_all_images(user) or image.created_by_id == user.id


def image_list(request):
    selected_category_id = request.GET.get("category")
    categories = Category.objects.order_by("name")
    images = ImageItem.objects.select_related("category").order_by("-uploaded_at")

    if selected_category_id:
        images = images.filter(category_id=selected_category_id)

    context = {
        "images": images,
        "categories": categories,
        "selected_category_id": selected_category_id,
    }
    return render(request, "gallery/image_list.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("image_list")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if next_url:
                return redirect(next_url)
            return redirect("image_list")
    else:
        form = AuthenticationForm()

    pending_approval = request.GET.get("pending") == "1"
    return render(
        request,
        "gallery/login.html",
        {"form": form, "next": next_url, "pending_approval": pending_approval},
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("image_list")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            return redirect("/login/?pending=1")
    else:
        form = SignUpForm()

    return render(request, "gallery/signup.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("image_list")


@login_required
def image_upload(request):
    if request.method == "POST":
        form = ImageItemForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.created_by = request.user
            image.save()
            return redirect("image_list")
    else:
        form = ImageItemForm()

    return render(request, "gallery/image_upload.html", {"form": form})


@login_required
def image_update(request, pk):
    image = get_object_or_404(ImageItem, pk=pk)
    if not _can_manage_image(request.user, image):
        raise PermissionDenied

    if request.method == "POST":
        form = ImageItemForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect("image_detail", pk=image.pk)
    else:
        form = ImageItemForm(instance=image)

    return render(
        request,
        "gallery/image_form.html",
        {"form": form, "image": image, "page_title": "이미지 수정", "submit_label": "저장"},
    )


@login_required
def image_delete(request, pk):
    image = get_object_or_404(ImageItem, pk=pk)
    if not _can_manage_image(request.user, image):
        raise PermissionDenied

    if request.method == "POST":
        image.delete()
        return redirect("image_list")

    return render(request, "gallery/image_confirm_delete.html", {"image": image})


def image_detail(request, pk):
    image = get_object_or_404(ImageItem.objects.select_related("category"), pk=pk)
    if image.category_id:
        slides = list(
            ImageItem.objects.select_related("category")
            .filter(category_id=image.category_id)
            .order_by("-uploaded_at")
        )
    else:
        slides = list(
            ImageItem.objects.select_related("category")
            .filter(category__isnull=True)
            .order_by("-uploaded_at")
        )

    initial_index = 0
    for idx, slide in enumerate(slides):
        if slide.pk == image.pk:
            initial_index = idx
            break

    return render(
        request,
        "gallery/image_detail.html",
        {"image": image, "slides": slides, "initial_index": initial_index},
    )


@login_required
def image_category_update(request, pk):
    image = get_object_or_404(ImageItem.objects.select_related("category"), pk=pk)
    if not _can_manage_image(request.user, image):
        raise PermissionDenied

    if request.method == "POST":
        form = ImageCategoryUpdateForm(request.POST, instance=image)
        if form.is_valid():
            form.save()
            return redirect("image_detail", pk=image.pk)
    else:
        form = ImageCategoryUpdateForm(instance=image)

    return render(
        request,
        "gallery/image_category_form.html",
        {"form": form, "image": image},
    )


@login_required
def category_list(request):
    manage_all = _can_manage_all_categories(request.user)
    categories = Category.objects.annotate(image_count=Count("images")).order_by("name")
    if not manage_all:
        categories = categories.filter(created_by=request.user)

    return render(
        request,
        "gallery/category_list.html",
        {"categories": categories, "can_manage_all": manage_all},
    )


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(
        request,
        "gallery/category_form.html",
        {"form": form, "page_title": "분류 추가", "submit_label": "추가"},
    )


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not _can_manage_category(request.user, category):
        raise PermissionDenied

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return render(
        request,
        "gallery/category_form.html",
        {"form": form, "page_title": "분류 수정", "submit_label": "저장"},
    )


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if not _can_manage_category(request.user, category):
        raise PermissionDenied

    if request.method == "POST":
        category.delete()
        return redirect("category_list")
    return render(request, "gallery/category_confirm_delete.html", {"category": category})
