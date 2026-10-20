"""Identity records only; OTP, MFA and partner membership are later phases."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import Q


class UserRole(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    SUPPORT = "support", "Support"
    FINANCE = "finance", "Finance"
    ADMIN = "admin", "Administrator"
    PARTNER_VIEWER = "partner_viewer", "Partner viewer"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError("A user must have an email address or phone number")
        if email:
            email = self.normalize_email(email).strip().lower()
        if phone_number:
            phone_number = phone_number.strip()
        user = self.model(email=email or None, phone_number=phone_number or None, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("A superuser must have is_staff and is_superuser set to True")
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ("-date_joined", "id")
        constraints = [
            models.CheckConstraint(
                condition=Q(email__isnull=False) | Q(phone_number__isnull=False),
                name="accounts_user_has_email_or_phone",
            ),
        ]
        indexes = [models.Index(fields=("role", "is_active"), name="accounts_role_active_idx")]

    def __str__(self) -> str:
        return self.email or self.phone_number or f"User {self.pk}"
