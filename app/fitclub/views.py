from unicodedata import name
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from .models import *

def ini(request):
    group1 = Group(name = "admin")
    group1.save()
    group2 = Group(name = "trener")
    group2.save()
    
    return HttpResponse("OK")


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return HttpResponse(f"<h1>Hi, {request.user}!</h1>")


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="fitclub/registration.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("index")
            else:
                messages.error(request, "Неправельный логин или пароль!")
        else:
            messages.error(request, "Неправельный логин или пароль!")
    
    form = AuthenticationForm()
    return render(request=request, template_name="fitclub/login.html", context={"login_form": form})


def admin_users(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    User = get_user_model()
    users = User.objects.all()

    return render(request=request, template_name="fitclub/users.html", context={'users': users})


def user_info(request, id):
    User = get_user_model()
    user = User.objects.get(pk=id)
    return render(request=request, template_name="fitclub/user.html", context={'user': user})


def admin_groups(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    groups = SportGroup.objects.all()

    return render(request=request, template_name="fitclub/groups.html", context={'groups': groups})

@csrf_exempt
def add_group(request):
    if request.method == "POST":
        data = request.POST
        group_name = data.get("groupname")
        
        sport_group = SportGroup(name=group_name)
        sport_group.save()
        return redirect('groups')

    return render(request=request, template_name="fitclub/addgroup.html")

def group_info(request, id):
    group = SportGroup.objects.get(pk=id)
    User = get_user_model()
    tereners = User.objects.filter(groups__name='trener')

    return render(request=request, template_name="fitclub/group.html", context={'group': group, 'treners': tereners})
