from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from .models import EmailConfirm, User
from .forms import RegisterForm, LoginForm, ProfileForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})


def send_confirmation_email(user):
    code = randint(100000, 999999)
    EmailConfirm.objects.update_or_create(user=user, defaults={'code': code})
    try:
        send_mail(
            subject='Подтверждение email — DoriTJ',
            message=f'Привет {user.username}! Твой код: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
    except Exception as e:
        print("Email error:", e)
        



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                age=form.cleaned_data['age'],
                password=form.cleaned_data['password1'],
            )
            user.is_active = False
            user.save()
            send_confirmation_email(user)
            return render(request, 'confirm_email.html', {'username': user.username})
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if not user:
                not_active = User.objects.filter(
                    username=form.cleaned_data['username'],
                    is_active=False
                ).first()
                if not_active:
                    return render(request, 'login.html', {'form': form, 'error': 'Подтвердите email'})
                return render(request, 'login.html', {'form': form, 'error': 'Неверный логин или пароль'})
            
            login(request, user)

            if user.is_courier:
                return redirect('courier_dashboard')
            elif user.is_staff:
                return redirect('product_list')
            elif user.is_manager:
                return redirect('manager_dashboard')
            else:
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
    

def logout_user(request):
        logout(request)
        return redirect('login_user')
    
    

def confirm_email(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        code = request.POST.get('code')

        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'confirm_email.html', {'error': 'Пользователь не найден'})
        if user.is_active:
            return redirect('login_user')

        confirm = EmailConfirm.objects.filter(user=user, code=code).first()
        if not confirm:
            return render(request, 'confirm_email.html', {'error': 'Неверный код', 'username': username})

        user.is_active = True
        user.save()
        confirm.delete()
        return redirect('login_user')

    return render(request, 'confirm_email.html')


from django.utils.crypto import get_random_string

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            code = get_random_string(6, '0123456789')
            EmailConfirm.objects.update_or_create(
                user=user, defaults={'code': code}
            )
            try:
                send_mail(
                    subject='Восстановление пароля — DoriTJ',
                    message=f'Привет {user.username}! Твой код для сброса пароля: {code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email]
                )
            except Exception as e:
                print("Email error:", e)
        return render(request, 'reset_code.html', {'email': email})
    return render(request, 'forgot_password.html')


def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        code = request.POST.get('code', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if password1 != password2:
            return render(request, 'reset_code.html', {
                'email': email,
                'error': 'Пароли не совпадают'
            })

        user = User.objects.filter(email=email).first()
        if not user:
            return render(request, 'reset_code.html', {
                'email': email,
                'error': 'Пользователь не найден'
            })

        confirm = EmailConfirm.objects.filter(user=user, code=code).first()
        if not confirm:
            return render(request, 'reset_code.html', {
                'email': email,
                'error': 'Неверный код'
            })

        user.set_password(password1)
        user.save()
        confirm.delete()
        return redirect('login_user')

    return render(request, 'reset_code.html')