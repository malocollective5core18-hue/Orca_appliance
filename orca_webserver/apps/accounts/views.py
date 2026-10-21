"""Session-based entry points and role-routed ORCA account screens."""

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CustomerSignupForm, EmailLoginForm, StaffRegistrationForm
from .models import UserRole


def signup(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = CustomerSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("accounts:dashboard")
    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = EmailLoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.user)
        next_url = request.POST.get("next") or request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
            return redirect(next_url)
        return redirect("accounts:dashboard")
    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    is_customer = request.user.role == UserRole.CUSTOMER and not request.user.is_superuser
    is_admin = request.user.role == UserRole.ADMIN and not request.user.is_superuser
    may_register = request.user.is_superuser or is_admin
    return render(
        request,
        "accounts/dashboard.html",
        {
            "is_customer": is_customer,
            "is_admin": is_admin,
            "may_register": may_register,
            "role_label": "Superuser" if request.user.is_superuser else request.user.get_role_display(),
        },
    )


@login_required
def register_staff(request):
    if not (request.user.is_superuser or request.user.role == UserRole.ADMIN):
        return HttpResponseForbidden("You are not allowed to register system users.")
    form = StaffRegistrationForm(request.POST or None, creator=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return render(request, "accounts/register_staff.html", {"form": StaffRegistrationForm(creator=request.user), "created": True})
    return render(request, "accounts/register_staff.html", {"form": form})


@login_required
def operations_dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("This dashboard is for ORCA staff accounts.")
    demo_file = settings.BASE_DIR / "orca-dashboard-demo-1.html"
    page = demo_file.read_text(encoding="utf-8")
    users_url = reverse("accounts:register_staff") if (request.user.is_superuser or request.user.role == UserRole.ADMIN) else ""
    admin_url = reverse("admin:index") if request.user.is_superuser else ""
    account_nav = format_html(
        '<nav aria-label="Main" id="nav" data-account-users="{}" data-django-admin="{}" data-user-name="{}" data-user-email="{}" data-user-phone="{}" data-user-role="{}"></nav>',
        users_url, admin_url,
        request.user.full_name or request.user.email or request.user.phone_number,
        request.user.email, request.user.phone_number,
        "Superuser" if request.user.is_superuser else request.user.get_role_display(),
    )
    page = page.replace('<nav aria-label="Main" id="nav"></nav>', str(account_nav), 1)
    return HttpResponse(page, content_type="text/html; charset=utf-8")
