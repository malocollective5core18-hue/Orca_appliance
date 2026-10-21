from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("full_name", "email", "phone_number", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("full_name", "email", "phone_number")
    fieldsets = (
        (None, {"fields": ("full_name", "email", "phone_number", "password")}),
        (
            "Access",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("full_name", "email", "phone_number", "role", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ("date_joined", "last_login")
