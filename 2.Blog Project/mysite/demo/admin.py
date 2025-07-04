from django.contrib import admin # type: ignore
from .models import BlogPost

# Register your models here.
admin.site.register(BlogPost)