from django.contrib import admin
from django.urls import path, include
from inventory.views import DashboardView, LoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns=[
 path('admin/', admin.site.urls),
 path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
 path("accounts/logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
 path('', DashboardView.as_view(), name='dashboard'),
 path('inventory/', include('inventory.urls')),
]
