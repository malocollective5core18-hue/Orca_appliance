"""Forms for customer self-registration and tightly scoped staff account creation."""

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserRole

User = get_user_model()


class CustomerSignupForm(forms.Form):
    full_name = forms.CharField(max_length=160)
    email = forms.EmailField(max_length=254)
    phone_number = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirmation = cleaned.get("confirm_password")
        if password and confirmation and password != confirmation:
            self.add_error("confirm_password", "The passwords do not match.")
        if password:
            candidate = User(email=cleaned.get("email"), phone_number=cleaned.get("phone_number"))
            try:
                validate_password(password, candidate)
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            full_name=self.cleaned_data["full_name"].strip(),
            role=UserRole.CUSTOMER,
            password=self.cleaned_data["password"],
        )


class EmailLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("email") and cleaned.get("password"):
            self.user = authenticate(
                self.request,
                username=cleaned["email"].strip().lower(),
                password=cleaned["password"],
            )
            if self.user is None:
                raise forms.ValidationError("Email or password is incorrect.")
            if not self.user.is_active:
                raise forms.ValidationError("This account is inactive.")
        return cleaned


class StaffRegistrationForm(forms.Form):
    full_name = forms.CharField(max_length=160)
    email = forms.EmailField(max_length=254)
    phone_number = forms.CharField(max_length=32)
    role = forms.ChoiceField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def __init__(self, *args, creator, **kwargs):
        self.creator = creator
        super().__init__(*args, **kwargs)
        choices = [(UserRole.CUSTOMER_SERVICE, "Customer service")]
        if creator.is_superuser:
            choices += [
                (UserRole.CUSTOMER, "Customer"),
                (UserRole.ADMIN, "Administrator"),
                (UserRole.FINANCE, "Finance"),
                (UserRole.PARTNER_VIEWER, "Partner viewer"),
                (UserRole.SUPPORT, "Support"),
                (UserRole.SUPERUSER, "Superuser"),
            ]
        self.fields["role"].choices = choices

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"]).strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"].strip()
        if User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("An account with this phone number already exists.")
        return phone

    def clean_role(self):
        role = self.cleaned_data["role"]
        if not self.creator.is_superuser and role != UserRole.CUSTOMER_SERVICE:
            raise forms.ValidationError("Administrators may create customer service accounts only.")
        return role

    def save(self):
        role = self.cleaned_data["role"]
        is_superuser = role == UserRole.SUPERUSER
        is_staff = role in {
            UserRole.SUPERUSER,
            UserRole.ADMIN,
            UserRole.CUSTOMER_SERVICE,
            UserRole.FINANCE,
            UserRole.SUPPORT,
            UserRole.PARTNER_VIEWER,
        }
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            phone_number=self.cleaned_data["phone_number"],
            full_name=self.cleaned_data["full_name"].strip(),
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
            password=self.cleaned_data["password"],
        )
