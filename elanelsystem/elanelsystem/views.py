from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views import generic
from django.urls import reverse_lazy
from users.forms import CustomLoginForm

class IndexLoginView(generic.FormView):
    form_class = CustomLoginForm
    template_name = "index.html"
    success_url = reverse_lazy('sales:resumen')

    def form_valid(self, form):
        """
        Si el formulario es válido, inicia sesión en el usuario
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        else:
            print("nose logeo nati  ")
        return super().form_valid(form)
