from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Category, ImageItem


class ImageItemForm(forms.ModelForm):
    class Meta:
        model = ImageItem
        fields = ["title", "category", "image"]


class ImageCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = ImageItem
        fields = ["category"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "아이디"
        self.fields["password1"].label = "비밀번호"
        self.fields["password2"].label = "비밀번호 확인"
        self.fields["username"].help_text = ""
        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
