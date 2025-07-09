from django import forms  # type: ignore
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Book


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'cover']

class RegisterForm(UserCreationForm):
    email =forms.EmailField(required=True)

    class META:
        model=User
        fields=['username','email','password1','password2']
