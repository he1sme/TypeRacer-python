from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("test/", views.test, name="test"),
    path("api/submit/", views.submit_result, name="submit_result"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),

    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("login/", auth_views.LoginView.as_view(template_name="typingtest/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
