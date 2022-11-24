from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from .forms import NewUserForm
from .models import *
import datetime


DAYS = [
    '',
    'Понедельник',
    'Вторник',
    'Среда',
    'Четверг',
    'Пятница',
    'Суббота',
    'Воскресенье'
]

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
    users = User.objects.filter(
    groups__name__in=['trener', 'admin'])
    return render(request=request, template_name="fitclub/users.html", context={'users': users})

@csrf_exempt
def user_info(request, id):
    User = get_user_model()
    user = User.objects.get(pk=id)

    if request.method == "POST":
        data = request.POST
        
        role = data['role']
        group = Group.objects.get(name=role)
        user.groups.clear()
        user.groups.add(group)

        user.save()
    if len(user.groups.all()) > 0:
        rl = user.groups.all()[0].name
    else:
        rl = "none"
    

    

    return render(request=request, template_name="fitclub/user.html", context={'user': user, 'rl': rl})


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

@csrf_exempt
def group_info(request, id):
    User = get_user_model()
    if request.method == "POST":
        data = request.POST
        group = SportGroup.objects.get(pk=id)

        group_trener_pk = data.get("new_trener")

        if group_trener_pk == 'none':
            if group.trener != None:
                group.trener = None
        else:
            group_trener_pk = int(group_trener_pk)
            if not group.trener or (group_trener_pk != group.trener.pk):
                new_trener  = User.objects.get(pk=group_trener_pk)
                group.trener = new_trener

        group_name = data.get("groupname")

        if group.name != group_name:
            group.name = group_name

        if "addtime" in data:
            return redirect('newtime', group_id=id)
        
        if "edittime" in data:
            return redirect('edittime', time_id=int(data['edittime']))

        group.save()


    group = SportGroup.objects.get(pk=id)
    tereners = User.objects.filter(groups__name='trener')

    clients = Client.objects.filter(groups=group.pk)

    times = GroupTime.objects.filter(group=group.pk).order_by('day')

    days = []
    for time in times:
        days.append((DAYS[time.day], time))

    return render(request=request, template_name="fitclub/group.html", context={'group': group, 'treners': tereners, 'clients': clients, 'days': days})


def admin_clients(request):
    if not request.user.is_authenticated:
        return redirect('login')

    clients = Client.objects.all()

    return render(request=request, template_name="fitclub/clients.html", context={'clients': clients})

@csrf_exempt
def client_info(request, id):
    client = Client.objects.get(pk=id)
    groups = SportGroup.objects.all()
    if request.method == "POST":
        data = request.POST
        
        client.groups.clear()
        for g in groups:
            if f'clientgroup{g.pk}' in data:
                client.groups.add(g)

    return render(request=request, template_name="fitclub/client.html", context={'user': client, 'gruops': groups})

@csrf_exempt
def add_new_time(request, group_id):
    group = SportGroup.objects.get(pk=group_id)

    if request.method == "POST":
        data = request.POST
        ts = datetime.time(*(map(int, data['starttime'].split(':'))))
        te = datetime.time(*(map(int, data['endtime'].split(':'))))
        day_num = int(data['day'])

        group_time = GroupTime(start=ts, end=te, day=day_num, group=group)
        group_time.save()
        return redirect('group', id=group_id)

    return render(request=request, template_name="fitclub/new_time.html", context={'group': group})


@csrf_exempt
def edit_time(request, time_id):
    time = GroupTime.objects.get(pk=time_id)
    group = SportGroup.objects.get(pk=time.group.pk)

    if request.method == "POST":
        data = request.POST
        ts = datetime.time(*(map(int, data['starttime'].split(':'))))
        te = datetime.time(*(map(int, data['endtime'].split(':'))))
        day_num = int(data['day'])

        time.start = ts
        time.end = te
        time.day = day_num
        time.save()

        return redirect('group', id=group.pk)

    ts = ""
    if len(str(time.start.hour)) == 1:
        ts += "0" + str(time.start.hour) + ":"
    else:
        ts += str(time.start.hour) + ":"

    if len(str(time.start.minute)) == 1:
        ts += "0" + str(time.start.minute)
    else:
        ts += str(time.start.minute)

    te = ""
    if len(str(time.end.hour)) == 1:
        te += "0" + str(time.end.hour) + ":"
    else:
        te += str(time.end.hour) + ":"

    if len(str(time.end.minute)) == 1:
        te += "0" + str(time.end.minute)
    else:
        te += str(time.end.minute)
    
    d = DAYS[time.day]

    return render(request=request, template_name="fitclub/edit_time.html", context={'group': group, 'start': ts, 'end': te, 'day': d})
