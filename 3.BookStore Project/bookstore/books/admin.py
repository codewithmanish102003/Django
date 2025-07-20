from django.contrib import admin  # type: ignore
from django.contrib.auth.admin import UserAdmin  # type: ignore

from .models import Book, CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )

admin.site.register(Book)
admin.site.register(CustomUser, CustomUserAdmin)