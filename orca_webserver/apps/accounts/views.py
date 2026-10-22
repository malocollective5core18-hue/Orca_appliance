"""Session-based entry points and role-routed ORCA account screens."""

from html import escape

from django.conf import settings
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST, require_safe

from .forms import CustomerSignupForm, EmailLoginForm, StaffRegistrationForm, StaffUserUpdateForm
from .models import User, UserRole


def _safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}, request.is_secure()):
        return next_url
    return ""


def signup(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request) or "accounts:dashboard")
    form = CustomerSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(_safe_next_url(request) or "accounts:dashboard")
    return render(request, "accounts/signup.html", {"form": form, "next": _safe_next_url(request)})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request) or "accounts:dashboard")
    form = EmailLoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.user)
        return redirect(_safe_next_url(request) or "accounts:dashboard")
    return render(request, "accounts/login.html", {"form": form, "next": _safe_next_url(request)})


@require_POST
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("home")


@never_cache
@login_required
@require_safe
def mobile_entry(request):
    return render(request, "accounts/mobile_entry.html", {"user_name": request.user.full_name or request.user.email or request.user.phone_number})


@login_required
@require_safe
@never_cache
def mobile_web(request):
    demo_file = settings.BASE_DIR / "orca_web_mobile.html"
    page = demo_file.read_text(encoding="utf-8")
    display_name = request.user.full_name or request.user.email or request.user.phone_number or "ORCA customer"
    page = page.replace("__ORCA_USER_NAME__", escape(display_name))
    return HttpResponse(page, content_type="text/html; charset=utf-8")

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


def _can_manage_users(user):
    return user.is_superuser or user.role == UserRole.ADMIN


def _managed_users(user):
    users = User.objects.all()
    if not user.is_superuser:
        users = users.filter(role=UserRole.CUSTOMER_SERVICE, is_superuser=False)
    return users


@login_required
@require_GET
def staff_users(request):
    if not _can_manage_users(request.user):
        return JsonResponse({"detail": "You are not allowed to manage system users."}, status=403)
    users = _managed_users(request.user).order_by("full_name", "email", "phone_number")
    roles = list(UserRole.choices) if request.user.is_superuser else [(UserRole.CUSTOMER_SERVICE, "Customer service")]
    return JsonResponse({
        "users": [{
            "id": user.pk,
            "full_name": user.full_name,
            "email": user.email or "",
            "phone_number": user.phone_number or "",
            "role": user.role,
            "role_label": user.get_role_display(),
            "is_active": user.is_active,
            "date_joined": user.date_joined.strftime("%d %b %Y"),
        } for user in users],
        "roles": [{"value": value, "label": label} for value, label in roles],
    })


@login_required
@require_POST
def update_staff_user(request, user_id):
    if not _can_manage_users(request.user):
        return JsonResponse({"detail": "You are not allowed to manage system users."}, status=403)
    target = get_object_or_404(_managed_users(request.user), pk=user_id)
    form = StaffUserUpdateForm(request.POST, actor=request.user, target=target)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    updated = form.save()
    return JsonResponse({
        "ok": True,
        "user": {
            "id": updated.pk,
            "full_name": updated.full_name,
            "email": updated.email or "",
            "phone_number": updated.phone_number or "",
            "role": updated.role,
            "role_label": updated.get_role_display(),
            "is_active": updated.is_active,
            "date_joined": updated.date_joined.strftime("%d %b %Y"),
        },
    })


@login_required
def operations_dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("This dashboard is for ORCA staff accounts.")
    demo_file = settings.BASE_DIR / "orca-dashboard-demo-1.html"
    page = demo_file.read_text(encoding="utf-8")
    users_url = reverse("accounts:register_staff") if (request.user.is_superuser or request.user.role == UserRole.ADMIN) else ""
    admin_url = reverse("admin:index") if request.user.is_superuser else ""
    account_nav = format_html(
        '<nav aria-label="Main" id="nav" data-account-users="{}" data-account-users-list="{}" data-account-user-update="{}" data-django-admin="{}" data-csrf-token="{}" data-user-name="{}" data-user-email="{}" data-user-phone="{}" data-user-role="{}" data-user-status="{}" data-user-since="{}"></nav>',
        users_url, reverse("accounts:staff_users"), reverse("accounts:update_staff_user", args=[0]), admin_url, get_token(request),
        request.user.full_name or request.user.email or request.user.phone_number,
        request.user.email, request.user.phone_number,
        "Superuser" if request.user.is_superuser else request.user.get_role_display(),
        "Active" if request.user.is_active else "Inactive",
        request.user.date_joined.strftime("%d %b %Y"),
    )
    page = page.replace('<nav aria-label="Main" id="nav"></nav>', str(account_nav), 1)
    return HttpResponse(page, content_type="text/html; charset=utf-8")
