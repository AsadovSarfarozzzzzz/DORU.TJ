from django import forms
from .models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Логин',}))    
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder' : 'Age'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder' : '+992 XX XXX XXXX'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Enter your password again'}))
