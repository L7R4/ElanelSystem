from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.urls import reverse_lazy
from users.forms import CustomLoginForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from users.models import Usuario

class IndexLoginView(generic.FormView):
    form_class = CustomLoginForm
    template_name = "index.html"
    success_url = reverse_lazy('sales:resumen')

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        users = Usuario.objects.all()
        print(users)
        if request.user.is_authenticated:
            print("weps")
            return HttpResponseRedirect(self.get_success_url())
        else:
            print(request.user)
            return super(IndexLoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Si el formulario es válido, inicia sesión en el usuario
        """
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        print("weps3")
        if user is not None:
            print("weps4")
            login(self.request, user)
            return super(IndexLoginView, self).form_valid(form)


def logout_view(request):
    logout(request)
    return redirect('indexLogin')
