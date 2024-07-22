from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from user.models import *

def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'index.html')

def loginpage(request):
    return render(request, 'loginpage.html')

# superadmin
def loginaction(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if not user.is_active:
                messages.error(request, 'Account not activated, contact admin.')
                return redirect('loginpage')

            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    registered_users = User.objects.all()
                    return render(request, 'admin/adminhomepage.html', {'registered_users': registered_users})
                else:
                    login(request, user)
                    sessions = ChatSession.objects.filter(user=user).order_by('-created_at')
                    context = {
                        'sessions': sessions,
                        'chats': [],
                        'session_id': None,
                        'username': user.username,
                        'email': user.email
                    }
                    return render(request, 'user/userchat.html', context)
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('loginpage')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('loginpage')
    else:
        return render(request, 'loginpage.html')

def registeraction(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('registeraction')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('registeraction')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_superuser=False,
                is_staff=False,
                is_active=False
            )
            user.save()
            messages.success(request, 'Registration was successful.')
            return redirect('loginpage')
    else:
        return render(request, 'loginpage.html')

def user_logout(request):
    logout(request)
    return render(request, 'loginpage.html')