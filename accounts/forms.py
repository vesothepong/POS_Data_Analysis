from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        initial=Profile.ROLE_STAFF,
        widget=forms.RadioSelect,
        label="Account Role",
        help_text="Choose Administrator for full system control, or Staff for Point of Sale (POS) control.",
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "role")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role", Profile.ROLE_STAFF)
        if role == Profile.ROLE_ADMIN:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = True
            user.is_superuser = False
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
        return user
