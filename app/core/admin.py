"""
Django admin customization.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class VideoInline(admin.TabularInline):
    """List of videos in user admin page."""

    model = models.UserVideoRelation
    ordering = ["-collected"]
    fields = ["video", "collected"]
    readonly_fields = ["collected"]
    verbose_name = "Video"


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["-date_joined"]
    list_display = ["username", "email", "date_joined"]
    fieldsets = (
        (
            None,
            {
                "fields": ("username", "email", "password"),
            },
        ),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields = ["last_login", "date_joined"]
    inlines = [VideoInline]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "username",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


class VideoAdmin(admin.ModelAdmin):
    """Define Video in django-admin."""

    ordering = ["-todays", "-publish_date"]
    search_fields = ["title", "publish_date"]
    list_display = ["title", "publish_date", "todays"]


class UserVideoRelationAdmin(admin.ModelAdmin):
    """Define UserVideoRelation in django-admin."""

    ordering = ["-collected"]
    list_display = ["user", "video", "collected"]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.UserVideoRelation, UserVideoRelationAdmin)
