from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
class LoginView(BaseLoginView):
    template_name='registration/login.html'
class LogoutView(BaseLogoutView):
    pass
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name='inventory/dashboard.html'
