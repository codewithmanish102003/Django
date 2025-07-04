from django.contrib import admin # type: ignore
from .models import Book
# Register your models here.
admin.site.register(Book)