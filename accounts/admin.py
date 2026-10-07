from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile / Role"


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "get_role", "is_staff", "is_superuser")

    @admin.display(description="Role")
    def get_role(self, obj):
        return getattr(obj, "profile", None).get_role_display() if hasattr(obj, "profile") else "—"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at", "updated_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
