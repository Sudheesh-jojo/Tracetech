from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import  redirect
from django.contrib.auth.views import LoginView, LogoutView


class CustomLoginView(LoginView):
    template_name = 'accounts/loginpage.html'

    def form_valid(self, form):
        response= super().form_valid(form)
        if self.request.user.is_staff:
            return redirect('/admin/')
        else:
            return redirect('/reports/home/')

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):

        response = super().dispatch(request, *args, **kwargs)
        return redirect('login')

