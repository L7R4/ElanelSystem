from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class FormCreateUser(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Usuario
        fields =[
            'nombre',
            'email',
            'tel',
            'rango',
        ]