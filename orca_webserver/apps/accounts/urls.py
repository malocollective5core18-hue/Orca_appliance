from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/operations/", views.operations_dashboard, name="operations_dashboard"),
    path("dashboard/operations/demo/", views.operations_dashboard_demo, name="operations_dashboard_demo"),
    path("dashboard/register-user/", views.register_staff, name="register_staff"),
]
