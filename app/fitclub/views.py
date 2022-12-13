from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.db.models import Q
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
    ret = "OK\n"

    group1 = Group(name = "admin")
    group1.save()
    group2 = Group(name = "trener")
    group2.save()
    ret += "User groups\n"
    
    
    return HttpResponse(ret)


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

        user.first_name = data['clientname']
        user.last_name = data['clientsurname']
        user.email = data['clientemail']

        user.save()


    if len(user.groups.all()) > 0:
        rl = user.groups.all()[0].name
    else:
        rl = "none"    

    groups = SportGroup.objects.filter(trener=user)

    trenings = Trening.objects.filter(trener=user).order_by('-day', '-start')

    year = datetime.date.today().year
    month = datetime.date.today().month

    sums = []
    mnthtren = Trening.objects.filter(Q(trener=user) | Q(helper=user), day__year=str(year), day__month=str(month)).order_by('-day', '-start')

    sp = Param.objects.get(key="sum_from_late").value
    sa = Param.objects.get(key="sum_from_asist").value
    ss = Param.objects.get(key="sum_from_single").value
    sg = Param.objects.get(key="sum_from_group").value
    so = Param.objects.get(key="sum_from_one").value
    
    sm = 0
    
    for t in mnthtren:
        if t.progul == True:
            sums.append([sp, "Пропущенное занятие", t.day])
            sm += sp
        elif t.helper == user:
            sums.append([sa, "Помощь в качестве второго тренера", t.day])
            sm += sa
        else:
            if t.trening_type == "group":
                if t.col == 1:
                    sums.append([ss, "Групповое занятие", t.day])
                    sm += ss
                else:
                    sums.append([sg, "Групповое занятие", t.day])
                    sm += sg
            else:
                sums.append([so, "Персональная тренировка", t.day])
                sm += so

    return render(request=request, template_name="fitclub/user.html", context={'user': user, 'rl': rl, 'groups': groups, 'trenings': trenings, 'sums': sums, 'ym': f"{year}-{month}", 'sm': sm})


@csrf_exempt
def user_info_zp(request, id, month, year):
    User = get_user_model()
    user = User.objects.get(pk=id)

    if request.method == "POST":
        data = request.POST
        
        role = data['role']
        group = Group.objects.get(name=role)
        user.groups.clear()
        user.groups.add(group)

        user.first_name = data['clientname']
        user.last_name = data['clientsurname']
        user.email = data['clientemail']

        user.save()


    if len(user.groups.all()) > 0:
        rl = user.groups.all()[0].name
    else:
        rl = "none"    

    groups = SportGroup.objects.filter(trener=user)

    trenings = Trening.objects.filter(trener=user).order_by('-day', '-start')
    
    
    sums = []
    mnthtren = Trening.objects.filter(Q(trener=user) | Q(helper=user), day__year=str(year), day__month=str(month)).order_by('-day', '-start')

    sp = Param.objects.get(key="sum_from_late").value
    sa = Param.objects.get(key="sum_from_asist").value
    ss = Param.objects.get(key="sum_from_single").value
    sg = Param.objects.get(key="sum_from_group").value
    so = Param.objects.get(key="sum_from_one").value
    
    sm = 0
    
    for t in mnthtren:
        if t.progul == True:
            sums.append([sp, "Пропущенное занятие"])
            sm += sp
        elif t.helper == user:
            sums.append([sa, "Помощь в качестве второго тренера"])
            sm += sa
        else:
            if t.trening_type == "group":
                if t.col == 1:
                    sums.append([ss, "Групповое занятие"])
                    sm += ss
                else:
                    sums.append([sg, "Групповое занятие"])
                    sm += (sg * t.col)
            else:
                sums.append([so, "Персональная тренировка"])
                sm += so
    
    return render(request=request, template_name="fitclub/user.html", context={'user': user, 'rl': rl, 'groups': groups, 'trenings': trenings, 'sums': sums, 'ym': f"{year}-{month}", 'sm': sm, 'azp': True})


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

    trenings = Trening.objects.filter(group=group).order_by('-day', '-start')

    return render(request=request, template_name="fitclub/group.html", context={'group': group, 'treners': tereners, 'clients': clients, 'days': days, 'trenings':trenings})


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
            
        client.name = data['clientname']
        client.surname = data['clientsurname']
        client.phone = data['clientphone']
        client.email = data['clientemail']

        client.save()

    trenings = Trening.objects.filter(clients__id=client.pk).order_by('day', '-start')
    payments = Peyment.objects.filter(client__pk=id)
    
    plts = payments.all()
    
    trens = []
    for tren in trenings:
        print(type(plts))
        isp = False
        if tren.trening_type == "personal":
            if plts.filter(pay_type="one_month", date__month=tren.day.month):
                isp = True
            elif plts.filter(pay_type="one", date=tren.day):
                plts = plts.exclude(pk=plts.filter(pay_type="one", date=tren.day).first().pk)
                isp = True
        if tren.trening_type == "group":
            if plts.filter(pay_type="group_month", date__month=tren.day.month):
                isp = True
            elif plts.filter(pay_type="group", date=tren.day):
                plts = plts.exclude(pk=plts.filter(pay_type="group", date=tren.day).first().pk)
                isp = True
        
        trens.append([tren, isp])
    
    return render(request=request, template_name="fitclub/client.html", context={'user': client, 'gruops': groups, 'trenings': trens, 'payments': payments})

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


@csrf_exempt
def new_trening(request, group_id):
    User = get_user_model()
    group = SportGroup.objects.get(pk=group_id)
    clients = Client.objects.filter(groups=group.pk)
    if request.method == "POST":
        data = request.POST

        ts = datetime.time(*(map(int, data['starttime'].split(':'))))
        te = datetime.time(*(map(int, data['endtime'].split(':'))))

        dt = datetime.date(*(map(int, data['date'].split('-'))))

        trener = User.objects.get(pk=int(data['trener']))
        if 'helper' in data:
            helper = User.objects.get(pk=int(data['helper']))
        else:
            helper = None
        
        col = 0
        parcts = []
        for cl in clients:
            if f'clientgroup{cl.pk}' in data:
                col += 1
                parcts.append(cl)
        
        progul = True if col == 0 else False
        
        trening = Trening(start=ts, end=te, day=dt, group=group, trening_type="group", col=col, is_was=True, progul=progul, trener=trener, helper=helper)
        trening.save()
        trening.clients.add(*parcts)
        trening.save()

        return redirect('group', id=group_id)

    treniers = User.objects.filter(groups__name='trener')

    rl = ""
    if len(request.user.groups.all()) > 0:
        rl = request.user.groups.all()[0].name
    else:
        rl = "none"

    return render(request=request, template_name="fitclub/new_trening.html", context={'group': group, 'user': request.user, 'treniers': treniers, 'rl': rl, 'clients': clients})


def admin_trenings(request):
    treinings = Trening.objects.all().order_by('-day', '-start')

    return render(request=request, template_name='fitclub/trenings.html', context={'trenings': treinings})

@csrf_exempt
def info_trenings(request, id):
    trening = Trening.objects.get(pk=id)
    if trening.trening_type == "group":
        clients = Client.objects.filter(groups=trening.group.pk)

        if request.method == "POST":
            data = request.POST

            ts = datetime.time(*(map(int, data['starttime'].split(':'))))
            te = datetime.time(*(map(int, data['endtime'].split(':'))))

            dt = datetime.date(*(map(int, data['date'].split('-'))))

            trener = User.objects.get(pk=int(data['trener']))
            if 'helper' in data:
                if data['helper'] != "none":
                    helper = User.objects.get(pk=int(data['helper']))
                else:
                    helper = None
            else:
                helper = None
            
            col = 0
            parcts = []

            for cl in clients:
                if f'clientgroup{cl.pk}' in data:
                    col += 1
                    parcts.append(cl)
            
            progul = True if col == 0 else False
            
            trening.start = ts
            trening.end = te
            trening.day = dt
            trening.trening_type = "group"
            trening.col = col
            trening.is_was = True
            trening.progul = progul
            trening.trener = trener
            trening.helper = helper
            trening.clients.clear()
            if col > 0:
                trening.clients.add(*parcts)
            trening.save()
        

        treniers = User.objects.filter(groups__name='trener')
        pr = []
        for cl in trening.clients.all():
            pr.append(cl.pk)

        return render(request=request, template_name="fitclub/edit_trening.html", context={'trening': trening, 'treniers': treniers, 'clients': clients, 'pr': pr})
    else:
        client = Client.objects.get(pk=trening.clients.all()[0].pk)

        if request.method == "POST":
            data = request.POST

            ts = datetime.time(*(map(int, data['starttime'].split(':'))))
            te = datetime.time(*(map(int, data['endtime'].split(':'))))

            dt = datetime.date(*(map(int, data['date'].split('-'))))

            trener = User.objects.get(pk=int(data['trener']))
            if 'helper' in data:
                if data['helper'] != "none":
                    helper = User.objects.get(pk=int(data['helper']))
                else:
                    helper = None
            else:
                helper = None
            
            progul = False
            if "progul" in data:
                progul = True

            col = 0 if progul else 1

            trening.start = ts
            trening.end = te
            trening.day = dt
            trening.trening_type = "personal"
            trening.col = col
            trening.is_was = True
            trening.progul = progul
            trening.trener = trener
            trening.helper = helper
            trening.save()
        

        treniers = User.objects.filter(groups__name='trener')

        return render(request=request, template_name="fitclub/edit_trening.html", context={'trening': trening, 'treniers': treniers, 'client': client})


def week_plan(request):
    
    times = GroupTime.objects.all()

    return render(request=request, template_name="fitclub/calendar.html", context={'times': times})


def calendar(request, date='today', view='month'):
    trenings = Trening.objects.all()
    if date == 'today':
        date = datetime.date.today().strftime("%Y-%m-%d")

    dt = date.split('-')
    dt[1] = str(int(dt[1]) - 1)

    return render(request=request, template_name="fitclub/cal.html", context={'trenings': trenings, 'view': view, 'date': dt})


@csrf_exempt
def new_per(request, id):
    User = get_user_model()
    client = Client.objects.get(pk=id)
    if request.method == "POST":
        data = request.POST

        ts = datetime.time(*(map(int, data['starttime'].split(':'))))
        te = datetime.time(*(map(int, data['endtime'].split(':'))))

        dt = datetime.date(*(map(int, data['date'].split('-'))))

        trener = User.objects.get(pk=int(data['trener']))
        if 'helper' in data:
            helper = User.objects.get(pk=int(data['helper']))
        else:
            helper = None
        
        progul = False
        if "progul" in data:
            progul =  True

        col = 0 if progul else 1
        
        trening = Trening(start=ts, end=te, day=dt, group=None, trening_type="personal", col=col, is_was=True, progul=progul, trener=trener, helper=helper)
        trening.save()
        trening.clients.add(client)
        trening.save()

        return redirect('client', id=id)

    treniers = User.objects.filter(groups__name='trener')

    rl = ""
    if len(request.user.groups.all()) > 0:
        rl = request.user.groups.all()[0].name
    else:
        rl = "none"

    return render(request=request, template_name="fitclub/new_per.html", context={'client': client, 'user': request.user, 'treniers': treniers, 'rl': rl})


@csrf_exempt
def new_pay(request, type, client_id):
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        data = request.POST

        if type == "one":
            price = Param.objects.get(key="prise_one")
            way = "card"
            if data['role'] == "money":
                way = "cash"
            date = datetime.date(*(map(int, data['date'].split('-'))))

            pay = Peyment(client=client, way=way, pay_type="one", date=date, value=price.value)
            pay.save()
            return redirect('client', id=client_id)
        
        if type == "one_month":
            price = Param.objects.get(key="price_one_month")
            way = "card"
            if data['role'] == "money":
                way = "cash"
            date = datetime.date(*(map(int, data['date'].split('-'))))

            pay = Peyment(client=client, way=way, pay_type="one_month", date=date, value=price.value)
            pay.save()
            return redirect('client', id=client_id)
        
        if type == "group":
            price = Param.objects.get(key="price_group")
            way = "card"
            if data['role'] == "money":
                way = "cash"
            date = datetime.date(*(map(int, data['date'].split('-'))))
            group = SportGroup.objects.get(pk=int(data['group']))
            pay = Peyment(client=client, way=way, pay_type="group", group=group, date=date, value=price.value)
            pay.save()
            return redirect('client', id=client_id)
        
        if type == "group_month":
            price = Param.objects.get(key="price_group_month")
            way = "card"
            if data['role'] == "money":
                way = "cash"
            date = datetime.date(*(map(int, data['date'].split('-'))))
            group = SportGroup.objects.get(pk=int(data['group']))
            pay = Peyment(client=client, way=way, pay_type="group_month", group=group, date=date, value=price.value)
            pay.save()
            return redirect('client', id=client_id)


    if type == "one":
        price = Param.objects.get(key="prise_one")

        return render(request=request, template_name="fitclub/new_pay.html", context={'client': client, 'type': type, 'price': price})
    
    if type == "one_month":
        price = Param.objects.get(key="price_one_month")

        return render(request=request, template_name="fitclub/new_pay.html", context={'client': client, 'type': type, 'price': price})
    
    if type == "group":
        price = Param.objects.get(key="price_group")

        return render(request=request, template_name="fitclub/new_pay.html", context={'client': client, 'type': type, 'price': price, 'groups': client.groups.all()})
    
    if type == "group_month":
        price = Param.objects.get(key="price_group_month")

        return render(request=request, template_name="fitclub/new_pay.html", context={'client': client, 'type': type, 'price': price, 'groups': client.groups.all()})


def selary(request):
    User = get_user_model()
    users = User.objects.filter(
    groups__name__in=['trener'])
    
    year = datetime.date.today().year
    month = datetime.date.today().month
    
    usrs = []
    for user in users:
        selrs = Salary.objects.filter(user=user, date__year=str(year), date__month=str(month))
        allselrs = Salary.objects.filter(user=user)
        
        gv = 0
        for sl in selrs:
            gv += sl.give
        
        allgv = 0
        for sl in allselrs:
            allgv += sl.give
        
        mnthtren = Trening.objects.filter(Q(trener=user) | Q(helper=user), day__year=str(year), day__month=str(month)).order_by('-day', '-start')

        sp = Param.objects.get(key="sum_from_late").value
        sa = Param.objects.get(key="sum_from_asist").value
        ss = Param.objects.get(key="sum_from_single").value
        sg = Param.objects.get(key="sum_from_group").value
        so = Param.objects.get(key="sum_from_one").value
        
        sm = 0
        
        for t in mnthtren:
            if t.progul == True:
                sm += sp
            elif t.helper == user:
                sm += sa
            else:
                if t.trening_type == "group":
                    if t.col == 1:
                        sm += ss
                    else:
                        sm += sg
                else:
                    sm += so
                    
        
        mnthtrena = Trening.objects.filter(Q(trener=user) | Q(helper=user))
        sma = 0
        
        for t in mnthtrena:
            if t.progul == True:
                sma += sp
            elif t.helper == user:
                sma += sa
            else:
                if t.trening_type == "group":
                    if t.col == 1:
                        sma += ss
                    else:
                        sma += sg
                else:
                    sma += so

        usrs.append([user, sm, gv, sma - allgv])
    
    return render(request=request, template_name="fitclub/selary.html", context={'users': usrs, 'ym': f"{year}-{month}"})


@csrf_exempt
def new_selary(request, id):
    User = get_user_model()
    user = User.objects.get(pk=id)
    
    if request.method == "POST":
        data = request.POST
        col = int(data['col'])
        
        selr = Salary(user=user, date=datetime.date.today(), give=col, accure=-1)
        selr.save()  
        return redirect('selary')   

    return render(request=request, template_name="fitclub/newsalary.html", context={'user': user})


def prselary(request, month, year):
    User = get_user_model()
    users = User.objects.filter(
    groups__name__in=['trener'])
    
    if year == datetime.date.today().year and month == datetime.date.today().month:
        return redirect('selary')
    
    usrs = []
    for user in users:
        selrs = Salary.objects.filter(user=user, date__year=str(year), date__month=str(month))
        
        gv = 0
        for sl in selrs:
            gv += sl.give
        
        mnthtren = Trening.objects.filter(Q(trener=user) | Q(helper=user), day__year=str(year), day__month=str(month)).order_by('-day', '-start')

        sp = Param.objects.get(key="sum_from_late").value
        sa = Param.objects.get(key="sum_from_asist").value
        ss = Param.objects.get(key="sum_from_single").value
        sg = Param.objects.get(key="sum_from_group").value
        so = Param.objects.get(key="sum_from_one").value
        
        sm = 0
        
        for t in mnthtren:
            if t.progul == True:
                sm += sp
            elif t.helper == user:
                sm += sa
            else:
                if t.trening_type == "group":
                    if t.col == 1:
                        sm += ss
                    else:
                        sm += sg
                else:
                    sm += so

        usrs.append([user, sm, gv])
    
    return render(request=request, template_name="fitclub/selary.html", context={'pr': True, 'users': usrs, 'ym': f"{year}-{month}"})


def dohod(request):
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    week = datetime.date.today().isocalendar().week
    
    ins = 0
    pays = Peyment.objects.filter(date__year=str(year), date__month=str(month))
    for p in pays:
        ins += p.value
    
    User = get_user_model()
    users = User.objects.filter(
    groups__name__in=['trener'])
    zp = 0
    for user in users:
        selrs = Salary.objects.filter(user=user, date__year=str(year), date__month=str(month))
        for sl in selrs:
            zp += sl.give
    
    spnd = 0
    spendings = Spending.objects.filter(date__year=str(year), date__month=str(month)).order_by('-date')
    for s in spendings:
        spnd += s.value
    
    
    incomes = Income.objects.filter(date__year=str(year), date__month=str(month)).order_by('-date')
    for inc in incomes:
        ins += inc.value
    
    return render(request=request, template_name="fitclub/dohod.html", context={'incomes': incomes, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': f"{year}-{month}", 'day': f"{year}-{month}-{day}", 'week': f"{year}-W{week}", 'month': f"{year}-{month}"})


def prdohod(request, type, date):
    if type == "day":
        dt = datetime.date(*(map(int, date.split('-'))))
        ins = 0
        pays = Peyment.objects.filter(date=dt)
        for p in pays:
            ins += p.value
        
        User = get_user_model()
        users = User.objects.filter(
        groups__name__in=['trener'])
        zp = 0
        for user in users:
            selrs = Salary.objects.filter(user=user, date=dt)
            for sl in selrs:
                zp += sl.give
        
        spnd = 0
        spendings = Spending.objects.filter(date=dt).order_by('-date')
        for s in spendings:
            spnd += s.value
        
        incomes = Income.objects.filter(date=dt).order_by('-date')
        for inc in incomes:
            ins += inc.value
            
        return render(request=request, template_name="fitclub/prdohod.html", context={'incomes': incomes, 'type': type, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': date})

    if type == "week":
        dt = date.split('-')
        dts = datetime.date.fromisocalendar(int(dt[0]), int(dt[1].replace('W', '')), 1).strftime("%Y-%m-%d")
        dte = datetime.date.fromisocalendar(int(dt[0]), int(dt[1].replace('W', '')), 7).strftime("%Y-%m-%d")
        ins = 0
        pays = Peyment.objects.filter(date__range=[dts, dte])
        for p in pays:
            ins += p.value
        
        User = get_user_model()
        users = User.objects.filter(
        groups__name__in=['trener'])
        zp = 0
        for user in users:
            selrs = Salary.objects.filter(user=user, date__range=[dts, dte])
            for sl in selrs:
                zp += sl.give
        
        spnd = 0
        spendings = Spending.objects.filter(date__range=[dts, dte]).order_by('-date')
        for s in spendings:
            spnd += s.value

        incomes = Income.objects.filter(date__range=[dts, dte]).order_by('-date')
        for inc in incomes:
            ins += inc.value
            
        return render(request=request, template_name="fitclub/prdohod.html", context={'incomes': incomes, 'type': type, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': date})
    
    if type == "month":
        dt = date.split('-')
        month = dt[1]
        year = dt[0]
        ins = 0
        pays = Peyment.objects.filter(date__year=str(year), date__month=str(month))
        for p in pays:
            ins += p.value
        
        User = get_user_model()
        users = User.objects.filter(
        groups__name__in=['trener'])
        zp = 0
        for user in users:
            selrs = Salary.objects.filter(user=user, date__year=str(year), date__month=str(month))
            for sl in selrs:
                zp += sl.give
        
        spnd = 0
        spendings = Spending.objects.filter(date__year=str(year), date__month=str(month)).order_by('-date')
        for s in spendings:
            spnd += s.value
            
        incomes = Income.objects.filter(date__year=str(year), date__month=str(month)).order_by('-date')
        for inc in incomes:
            ins += inc.value
            
        return render(request=request, template_name="fitclub/prdohod.html", context={'incomes': incomes, 'type': type, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': date})



@csrf_exempt
def new_spend(request):
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        spend = Spending(key=data['name'], value=int(data['col']), spend_type="default", date=dt)
        spend.save()
        
        return redirect('dohod')

    td = datetime.date.today()

    return render(request=request, template_name="fitclub/newspend.html", context={'ym': td})


@csrf_exempt
def edit_spend(request, id):
    spd = Spending.objects.get(pk=id)
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        spd.key=data['name']
        spd.value=int(data['col'])
        spd.date=dt
        spd.save()
        
        return redirect('dohod')

    return render(request=request, template_name="fitclub/editspend.html", context={'spend': spd})


@csrf_exempt
def new_income(request):
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        income = Income(key=data['name'], value=int(data['col']), date=dt)
        income.save()
        
        return redirect('dohod')

    td = datetime.date.today()

    return render(request=request, template_name="fitclub/newspend.html", context={'ym': td, 'inc': True})


@csrf_exempt
def edit_income(request, id):
    income = Income.objects.get(pk=id)
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        income.key=data['name']
        income.value=int(data['col'])
        income.date=dt
        income.save()
        
        return redirect('dohod')

    return render(request=request, template_name="fitclub/editspend.html", context={'spend': income, 'inc': True})