from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("mobile/", views.mobile_entry, name="mobile_entry"),
    path("mobile/web/", views.mobile_web, name="mobile_web"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/operations/", views.operations_dashboard, name="operations_dashboard"),
    path("dashboard/register-user/", views.register_staff, name="register_staff"),
    path("dashboard/users/", views.staff_users, name="staff_users"),
    path("dashboard/users/<int:user_id>/", views.update_staff_user, name="update_staff_user"),
]
