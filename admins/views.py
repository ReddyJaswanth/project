from django.shortcuts import render
from django.contrib.auth.models import User

# Create your views here.
def adminhome(request):
    registered_users = User.objects.all()   
    return render(request, 'admin/adminhomepage.html', {'registered_users': registered_users})

def AdminActiveUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        User.objects.filter(email=id).update(is_active=True)
        registered_users = User.objects.all()
        return render(request, "admin/adminhomepage.html", {'registered_users': registered_users})
    
def AdmindeActiveUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        print(id)
        User.objects.filter(email=id).update(is_active=False)
        registered_users = User.objects.all()
        return render(request, "admin/adminhomepage.html", {'registered_users': registered_users})