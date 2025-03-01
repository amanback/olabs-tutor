from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from myapp import views
from myapp.views import index, signup_view
from myapp.views import login_view
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="myapp/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("myapp.urls")),
    path("", include("myapp.urls")),   # Import your views
    path("", index, name="index"),  # Ensure this points to your question listing page
    path("signup/", signup_view, name="signup"),
    path('', index, name='index'),
    path("login/", login_view, name="login"),



]
