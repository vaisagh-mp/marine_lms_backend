from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Position, ShipType


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ShipType)
class ShipTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone_number", "position", "ship_type", "role", "is_active")
    list_filter = ("role", "position", "ship_type", "is_active", "is_staff")
    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "phone_number")}),
        ("Job info", {"fields": ("position", "ship_type", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(User, CustomUserAdmin)
