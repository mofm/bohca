from django import forms
from django.contrib.auth import get_user_model
from .models import BookmarkCategory, BookmarkTags


class CategoryForm(forms.ModelForm):
    """Bookmark Category Form"""

    class Meta:
        model = BookmarkCategory
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'


class TagForm(forms.ModelForm):
    """Bookmark Tag Form"""

    class Meta:
        model = BookmarkTags
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'


class UserUpdateForm(forms.ModelForm):
    """User Update Form"""
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for myField in self.fields:
            self.fields[myField].widget.attrs['class'] = 'form-control'
