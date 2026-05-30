from django import forms
from .models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Логин',}))    
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',}))
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder' : 'Age'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder' : '+992 XX XXX XXXX'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Enter your password again'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Логин уже занят')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email уже используется')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Your password'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логин'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': '+992 XX XXX XXXX'}),
            'address': forms.Textarea(attrs={'placeholder': 'Адрес доставки', 'rows': 2}),
        }
    
    
