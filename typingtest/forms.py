from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-950 border border-slate-800 outline-none focus:border-slate-500", "placeholder": "username"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-950 border border-slate-800 outline-none focus:border-slate-500", "placeholder": "password"}),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "w-full p-3 rounded-xl bg-slate-950 border border-slate-800 outline-none focus:border-slate-500", "placeholder": "repeat password"}),
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
