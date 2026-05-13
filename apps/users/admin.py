from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("username",)
    list_display = (
        "username",
        "email",
        "role",
        "module",
        "is_active",
        "is_staff",
        "created_at",
    )
    readonly_fields = ("created_at", "last_login", "date_joined")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("STUD", {"fields": ("role", "module", "is_first_login", "created_at")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("STUD", {"fields": ("role", "module", "is_first_login")}),
    )
