from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "staff"
    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrator (Full Control)"),
        (ROLE_STAFF, "Staff (POS Control)"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_STAFF,
        help_text="User role: Admin has full system control; Staff controls POS.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Automatically ensure every User has a matching Profile with correct role."""
    if created:
        role = Profile.ROLE_ADMIN if instance.is_superuser else Profile.ROLE_STAFF
        Profile.objects.create(user=instance, role=role)
    else:
        profile = getattr(instance, "profile", None)
        if profile is None:
            role = Profile.ROLE_ADMIN if instance.is_superuser else Profile.ROLE_STAFF
            Profile.objects.create(user=instance, role=role)
        elif instance.is_superuser and profile.role != Profile.ROLE_ADMIN:
            profile.role = Profile.ROLE_ADMIN
            profile.save(update_fields=["role", "updated_at"])
