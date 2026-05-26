from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from random import randint
from .models import EmailConfirm, User
from django.core.mail import send_mail
from django.conf import settings




def send_confirmation_email(user):
    code = randint(100000, 999999)

    EmailConfirm.objects.update_or_create(user=user, defaults={'code':code})

    try:
        send_mail(
            subject='Confirm ur password',
            message=f'Hello mr(s) {user.username} Welcome to our dangerous web application plz confirm ur password {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
    except Exception as e:
         print(e, '========================================')
        



def register(request):

    if request.method=="POST":
        username = request.POST.get('username').strip()
        password1 = request.POST.get('password1').strip()
        password2 = request.POST.get('password2').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        age = request.POST.get('age').strip()

        if not username or not email or not password1 or not age or not phone:
            return render(request, 'accounts/register.html', {'error': 'All info are requeired'})

        if password1!=password2:
            return render(request, 'accounts/register.html', {'error': 'Password doesnt match'})
        elif User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Email already exists'})
        

        user = User.objects.create_user(username=username, email=email,
                                        password=password1, age=age, phone=phone)

        user.is_active = False
        user.save()
        send_confirmation_email(user)
        return render(request,'accounts/confirm_email.html', {'username': user.username})
         
    
    else:
        return render(request, 'accounts/register.html')


def login_user(request):
    
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if not user:
            not_active = User.objects.filter(username=username, is_active=False).first()
            if not_active:
                return render(request, 'accounts/login.html', {'error':'go and confirm ur email  '})
            else:
                return render(request, 'accounts/login.html', {'error':'Wrong password or username '})
        else:

            login(request, user)
            return redirect('/')
    
    else:
        return render(request, 'accounts/login.html')
    

def logout_user(request):
        logout(request)
        return redirect('login')
    
    

def confirm_email(request):

    if request.method=='POST':

        username = request.POST.get('username')
        code = request.POST.get('code')

        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'accounts/confirm_email.html', {'error': 'Invalid username'})
        
        if user.is_active:
            return redirect('login')
        confirm = EmailConfirm.objects.filter(user=user, code=code).first()

        if not confirm:
            return render(request, 'accounts/confirm_email.html', {'error': 'Wrong code'})
        
        user.is_active= True
        user.save()
        confirm.delete()
        return redirect('login')
    
    else:
        return render(request, 'accounts/confirm_email.html')