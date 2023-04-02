from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from .forms import NewUserForm
from .models import *
import datetime
# import send_message bot
from .management.commands.bot import send_message

from .tasks import testshd, alert_subs




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
    # if not request.user.is_authenticated:
    #     return redirect('login')
    
    ret = "OK\n"

    # group1 = Group(name = "admin")
    # group1.save()
    # group2 = Group(name = "trener")
    # group2.save()
    # group3 = Group(name = "masager")
    # group3.save()

    ret += "User groups\n"
    
    
    return HttpResponse(ret)





def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    week = datetime.date.today().isocalendar().week
    
    return render(request=request, template_name="fitclub/index.html", context={'day': f"{year}-{month}-{day}", 'week': f"{year}-W{week}", 'month': f"{year}-{month}"})


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


def logoutpage(request):
    if not request.user.is_authenticated:
        return redirect('login')
    logout(request)
    return redirect('login')

def admin_users(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    User = get_user_model()
    users = User.objects.filter(
    groups__name__in=['trener', 'admin', 'masager'])
    return render(request=request, template_name="fitclub/users.html", context={'users': users})

@csrf_exempt
def user_info(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()
    user = User.objects.get(pk=id)

    if len(user.groups.all()) > 0:
        rl = user.groups.all()[0].name
    else:
        rl = "none"

    if request.method == "POST":
        data = request.POST

        user.first_name = data['clientname']
        user.last_name = data['clientsurname']
        user.email = data['clientemail']

        if rl == "admin":
            selary_type = data['selarytype']
            selary_valuse = data['selary']

            if selary_type == "none":
                if AdminSalary.objects.filter(user=user).exists():
                    AdminSalary.objects.filter(user=user).delete()
            else:
                if AdminSalary.objects.filter(user=user).exists():
                    AdminSalary.objects.filter(user=user).update(type=selary_type, value=selary_valuse)
                else:
                    AdminSalary.objects.create(user=user, type=selary_type, value=selary_valuse)

        user.save()


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
    
    smv = None
    if rl == "admin":
        if AdminSalary.objects.filter(user=user).exists():
            smv = AdminSalary.objects.get(user=user)

    

    return render(request=request, template_name="fitclub/user.html", context={'user': user, 'smv': smv, 'rl': rl, 'groups': groups, 'trenings': trenings, 'sums': sums, 'ym': f"{year}-{month}", 'sm': sm})


@csrf_exempt
def user_info_zp(request, id, month, year):
    if not request.user.is_authenticated:
        return redirect('login')
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
    if not request.user.is_authenticated:
        return redirect('login')
    
    groups = SportGroup.objects.all()

    return render(request=request, template_name="fitclub/groups.html", context={'groups': groups})

@csrf_exempt
def add_group(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        data = request.POST
        group_name = data.get("groupname")
        
        sport_group = SportGroup(name=group_name)
        sport_group.save()
        return redirect('groups')

    return render(request=request, template_name="fitclub/addgroup.html")

@csrf_exempt
def group_info(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()
    group = SportGroup.objects.get(pk=id)
    clients = Client.objects.filter(groups=group.pk)
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

        if "issend" in data:
            msgtxt = data['messagetxt']
            for cl in clients:
                if cl.tg:
                    send_message(cl.tg, msgtxt)

        group.save()


    tereners = User.objects.filter(groups__name='trener')



    times = GroupTime.objects.filter(group=group.pk).order_by('day')

    days = []
    for time in times:
        days.append((DAYS[time.day], time))

    trenings = Trening.objects.filter(group=group).order_by('-day', '-start')

    return render(request=request, template_name="fitclub/group.html", context={'group': group, 'treners': tereners, 'clients': clients, 'days': days, 'trenings':trenings})


def admin_clients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_authenticated:
        return redirect('login')

    clients = Client.objects.all()

    return render(request=request, template_name="fitclub/clients.html", context={'clients': clients})

@csrf_exempt
def client_info(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
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
    payments = Peyment.objects.filter(client__pk=id).order_by('-date')
    

    # get all Subscriptions where client is client and today is between start_date and end_date or num_sessions > 0
    subs = Subscription.objects.filter(client=client, start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today()) | Subscription.objects.filter(client=client, num_sessions__gt=0)

    # get count of SingleTren where client is client and trening is null and pay pay_type is one
    singl_col  = SingleTren.objects.filter(client=client, trening=None, pay__pay_type="one").count()
    groups_col = SingleTren.objects.filter(client=client, trening=None, pay__pay_type="group").count()


    # get all SingleTren where client is client and trening is not null
    single_trenings = SingleTren.objects.filter(client=client, trening__isnull=False)
    # get all Trening from single_trenings
    trens = [(tren.trening, True if tren.pay else False) for tren in single_trenings]

    # get all Subscriptions where client is client
    subscrs = Subscription.objects.filter(client=client)
    # get all Trening from subscrs
    trens += [(tren, True) for subscr in subscrs for tren in subscr.trenings.all()]
    trens.sort(key=lambda x: x[0].day, reverse=True)


    massages = Massage.objects.filter(client=client, trening__isnull=False).order_by('-trening__day', '-trening__start')
    mass = []
    for mas in massages:
        mass.append((mas.trening, True if mas.pay else False))


    massage_types = MassageTypes.objects.all()

    mas_pay_counts = []

    for mt in massage_types:
        mas_pay_counts.append((mt, Massage.objects.filter(client=client, trening__isnull=True, pay__isnull=False, pay__pay_type=f"massage_{mt.pk}").count()))

    mts = []
    for mt in massage_types:
        mts.append((mt, f"massage-{mt.pk}"))

    tgcode = client.pk + 4564
    return render(request=request, template_name="fitclub/client.html", context={'tgcode': tgcode, 'massage_types': mts, 'mas_cols': mas_pay_counts, 'massages': mass, 'trens': trens, 'singl_col': singl_col ,'groups_col': groups_col,'subs': subs, 'user': client, 'gruops': groups, 'payments': payments})

@csrf_exempt
def add_new_time(request, group_id):
    if not request.user.is_authenticated:
        return redirect('login')
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
    if not request.user.is_authenticated:
        return redirect('login')
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
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()
    group = SportGroup.objects.get(pk=group_id)
    clients = Client.objects.filter(groups=group.pk)
    allcl = Client.objects.all()
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
        
        # col = 0
        # parcts = []
        # for cl in clients:
        #     if f'clientgroup{cl.pk}' in data:
        #         col += 1
        #         parcts.append(cl)


        col = 0
        parcts = []
        std_dt = {}
        for cl in allcl:
            if f'clientgroup{cl.pk}' in data:
                if cl in clients:
                    if int(data[f'clientgroup{cl.pk}']) == 4:
                        col += 1
                    if int(data[f'clientgroup{cl.pk}']) in [0, 4]:
                        parcts.append(cl)
                    std_dt[cl.pk] = int(data[f'clientgroup{cl.pk}'])
                elif int(data[f'clientgroup{cl.pk}']) == 4:
                    col += 1
                    parcts.append(cl)
                    std_dt[cl.pk] = int(data[f'clientgroup{cl.pk}'])

        
        progul = True if col == 0 else False
        
        trening = Trening(start=ts, end=te, day=dt, group=group, trening_type="group", col=col, is_was=True, progul=progul, trener=trener, helper=helper, students_data=std_dt)
        trening.save()
        trening.clients.add(*parcts)
        trening.save()
        
        for client in trening.clients.all():

            sub = Subscription.objects.filter(client=client, 
            start_date__lte=dt, 
            end_date__gte=dt, num_sessions__gt=0, 
            tren_type="group").order_by('start_date').first()

            if sub:
                sub.trenings.add(trening)
                sub.num_sessions -= 1
                sub.save()
            else:
                sgt = SingleTren.objects.filter(client=client, 
                trening__isnull=True, 
                pay__pay_type='group').order_by('pay__date').first()

                if sgt:
                    sgt.trening = trening
                    sgt.save()
                else:
                    nsg = SingleTren(client=client, trening=trening, pay=None)
                    nsg.save()

        alert_subs.apply_async(args=(trening.pk, True), countdown=24*60*60)

        return redirect('group', id=group_id)
    
    treniers = User.objects.filter(groups__name='trener')

    rl = ""
    if len(request.user.groups.all()) > 0:
        rl = request.user.groups.all()[0].name
    else:
        rl = "none"

    # get all clients who not in group
    for cl in clients:
        allcl = allcl.exclude(pk=cl.pk)
        
    return render(request=request, template_name="fitclub/new_trening.html", context={'allcl': allcl, 'group': group, 'user': request.user, 'treniers': treniers, 'rl': rl, 'clients': clients})


def admin_trenings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    treinings = Trening.objects.all().order_by('-day', '-start')

    return render(request=request, template_name='fitclub/trenings.html', context={'trenings': treinings})

@csrf_exempt
def info_trenings(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    trening = Trening.objects.get(pk=id)

    if trening.trening_type.split('_')[0] == "massage":
        client = Client.objects.get(pk=trening.clients.all()[0].pk)

        if request.method == "POST":
            data = request.POST

            ts = datetime.time(*(map(int, data['starttime'].split(':'))))
            te = datetime.time(*(map(int, data['endtime'].split(':'))))

            dt = datetime.date(*(map(int, data['date'].split('-'))))

            trener = User.objects.get(pk=int(data['trener']))

            progul = False
            if "progul" in data:
                progul = True

            col = 0 if progul else 1

            mst_id = data['mastype']
            
            trening.start = ts
            trening.end = te
            trening.day = dt
            trening.trening_type = f"massage_{mst_id}"
            trening.col = col
            trening.is_was = True
            trening.progul = progul
            trening.trener = trener
            trening.save()

        treniers = User.objects.filter(groups__name='masager')
        tt = "massage"
        smt = MassageTypes.objects.get(pk=int(trening.trening_type.split('_')[1]))
        mt = MassageTypes.objects.all()
        return render(request=request, template_name="fitclub/edit_trening.html", context={'mt': mt,'smt': smt, 'tt': tt, 'trening': trening, 'treniers': treniers, 'client': client})


    if trening.trening_type == "group":
        clients = Client.objects.filter(groups=trening.group.pk)
        allcl = Client.objects.all()

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
            std_dt = {}
            for cl in allcl:
                if f'clientgroup{cl.pk}' in data:
                    if cl in clients:
                        if int(data[f'clientgroup{cl.pk}']) == 4:
                            col += 1
                        if int(data[f'clientgroup{cl.pk}']) in [0, 4]:
                            parcts.append(cl)
                        std_dt[cl.pk] = int(data[f'clientgroup{cl.pk}'])
                    elif int(data[f'clientgroup{cl.pk}']) == 4:
                        col += 1
                        parcts.append(cl)
                        std_dt[cl.pk] = int(data[f'clientgroup{cl.pk}'])

            # for cl in clients:
            #     if f'clientgroup{cl.pk}' in data:
            #         col += 1
            #         parcts.append(cl)
            
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
            trening.students_data = std_dt
            trening.clients.clear()
            if col > 0:
                trening.clients.add(*parcts)
            trening.save()

            
            sgtrs = SingleTren.objects.filter(trening=trening)
            for tr in sgtrs:
                if not tr.client in trening.clients.all():
                    if tr.pay is None:
                        tr.delete()
                    else:
                        tr.trening = None
                        tr.save()


            # get all subs where trening in subs.trenings
            subs = Subscription.objects.filter(trenings=trening)
            for sub in subs:
                if not sub.client in trening.clients.all():
                    sub.trenings.remove(trening)
                    sub.num_sessions += 1
                    sub.save()
            
            # get all subs where client in trening.clients
            clsubs = Subscription.objects.filter(client__in=trening.clients.all())
            for clsub in clsubs:
                if not clsub.trenings.filter(pk=trening.pk).first():
                    clsub.trenings.add(trening)
                    clsub.num_sessions -= 1
                    clsub.save()
            
            for client in trening.clients.all():
                if not SingleTren.objects.filter(trening=trening).first():
                    sgt = SingleTren.objects.filter(client=client, trening__isnull=True, pay__pay_type='group').order_by('pay__date').first()

                    if sgt:
                        sgt.trening = trening
                        sgt.save()
                    else:
                        nsg = SingleTren(client=client, trening=trening, pay=None)
                        nsg.save()
            

        treniers = User.objects.filter(groups__name='trener')


        treniers = User.objects.filter(groups__name='trener')

        rl = ""
        if len(request.user.groups.all()) > 0:
            rl = request.user.groups.all()[0].name
        else:
            rl = "none"

        # get all clients who not in group
        for cl in clients:
            allcl = allcl.exclude(pk=cl.pk)
        
        pr = trening.students_data
        return render(request=request, template_name="fitclub/edit_trening.html", context={'trening': trening, 'treniers': treniers, 'clients': clients, 'pr': pr, 'allcl': allcl})
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
            


            
            if int(data[f'clientgroup{cl.pk}']) == 4:
                col += 1
            if int(data[f'clientgroup{cl.pk}']) in [0, 4]:
                parcts.append(cl)
            std_dt[cl.pk] = int(data[f'clientgroup{cl.pk}'])


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
            trening.students_data = std_dt
            trening.save()



            sgtr = SingleTren.objects.filter(trening=trening).first()
            if not sgtr:
                subs = Subscription.objects.filter(client=client, trenings=trening).first()
                # check if dt between sub.start and sub.end
                if not (subs.start_date <= dt and dt <= subs.end_date):
                    sub = Subscription.objects.filter(client=client, start_date__lte=dt, end_date__gte=dt, num_sessions__gt=0, tren_type="single").order_by('start_date').first()

                    if sub:
                        # add to sub trenings trening and num sessions minus 1
                        sub.trenings.add(trening)
                        sub.num_sessions -= 1
                        sub.save()
            
                    else:
                        sgt = SingleTren.objects.filter(client=client, trening__isnull=True, pay__pay_type='one').order_by('pay__date').first()

                        if sgt:
                            sgt.trening = trening
                            sgt.save()
                        else:
                            nsg = SingleTren(client=client, trening=trening, pay=None)
                            nsg.save()
                    
                    subs.trenings.remove(trening)
                    subs.num_sessions += 1
                    subs.save()
                

        treniers = User.objects.filter(groups__name='trener')

        return render(request=request, template_name="fitclub/edit_trening.html", context={'trening': trening, 'treniers': treniers, 'client': client})


def week_plan(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    times = GroupTime.objects.all()

    return render(request=request, template_name="fitclub/calendar.html", context={'times': times})


def calendar(request, date='today', view='month'):
    if not request.user.is_authenticated:
        return redirect('login')
    trenings = Trening.objects.all()
    if date == 'today':
        date = datetime.date.today().strftime("%Y-%m-%d")

    dt = date.split('-')
    
    if len(dt[1]) == 1:
        dt[1] = '0' + dt[1]

    return render(request=request, template_name="fitclub/cal.html", context={'trenings': trenings, 'view': view, 'date': dt})


@csrf_exempt
def new_per(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
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


        # get Subscription where client is client and start_date <= dt and end_date >= dt and num_sessions > 0 and sport_group is None order by start_date
        sub = Subscription.objects.filter(client=client, start_date__lte=dt, end_date__gte=dt, num_sessions__gt=0, tren_type="single").order_by('start_date').first()

        if sub:
            # add to sub trenings trening and num sessions minus 1
            sub.trenings.add(trening)
            sub.num_sessions -= 1
            sub.save()
   
        else:
            sgt = SingleTren.objects.filter(client=client, trening__isnull=True, pay__pay_type='one').order_by('pay__date').first()

            if sgt:
                sgt.trening = trening
                sgt.save()
            else:
                nsg = SingleTren(client=client, trening=trening, pay=None)
                nsg.save()
        

        alert_subs.apply_async(args=(trening.pk, True), countdown=20)

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
    if not request.user.is_authenticated:
        return redirect('login')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        data = request.POST
        
        zal = None
        if 'zal' in data:
            zal_pk = data['zal']
            if zal_pk != 'none':
                zal = Zal.objects.get(pk=int(zal_pk))

        if type.split('-')[0] == "massage":
        
            col = int(data["col"])
            price = data["price"]
            
            mt = MassageTypes.objects.get(pk=int(type.split('-')[1]))
            for _ in range(col):
                way = "card"
                if data['role'] == "money":
                    way = "cash"
                if data['role'] == "site":
                    way = "site"

                date = datetime.date(*(map(int, data['date'].split('-'))))
                pay = Peyment(client=client, way=way, pay_type=f"massage_{mt.pk}", date=date, value=price, zal=zal)
                pay.save()
                

                notpayd = Massage.objects.filter(client=client, pay__isnull=True, trening__trening_type=f'massage_{mt.pk}').order_by('trening__day').first()
                if notpayd:
                    notpayd.pay = pay
                    notpayd.save()
                else:
                    sgtren = Massage(client=client, pay=pay, trening=None)
                    sgtren.save()
            return redirect('client', id=client_id)
        
        if type == "one":
        
            col = int(data["col"])
            for _ in range(col):
                price = data["price"]
                way = "card"
                if data['role'] == "money":
                    way = "cash"
                if data['role'] == "site":
                    way = "site"

                date = datetime.date(*(map(int, data['date'].split('-'))))

                pay = Peyment(client=client, way=way, pay_type="one", date=date, value=price, zal=zal)
                pay.save()
                
                
                notpayd = SingleTren.objects.filter(client=client, pay__isnull=True, trening__trening_type='personal').order_by('trening__day').first()
                if notpayd:
                    notpayd.pay = pay
                    notpayd.save()
                else:
                    sgtren = SingleTren(client=client, pay=pay, trening=None)
                    sgtren.save()
                    
            return redirect('client', id=client_id)

        if type == "one_month":
            price = data["price"]
            way = "card"
            if data['role'] == "money":
                way = "cash"
            if data['role'] == "site":
                    way = "site"

            date = datetime.date(*(map(int, data['date'].split('-'))))

            pay = Peyment(client=client, way=way, pay_type="one_month", date=date, value=data['price'], zal=zal)
            pay.save()
            
            
            startdate = datetime.date(*(map(int, data['startdate'].split('-'))))
            enddate = datetime.date(*(map(int, data['enddate'].split('-'))))
            sub = Subscription(start_date=startdate, end_date=enddate, num_sessions=int(data['col']), client=client, pay=pay, sport_group=None, tren_type="single")
            sub.save()
            
            # get all SingeTren where client is client and pay is null and trening is not null and trening day >= startdate and trening day <= enddate and trening trening_type is personal and order by trening day
            sgtrs = SingleTren.objects.filter(client=client, pay__isnull=True, trening__isnull=False, trening__day__gte=startdate, trening__day__lte=enddate, trening__trening_type='personal').order_by('trening__day')

            for tr in sgtrs:
                if sub.num_sessions <= 0:
                    break
                
                # add sub trenings tr trening and num sessions minus 1
                sub.trenings.add(tr.trening)
                sub.num_sessions -= 1
                
                tr.client = None
                tr.trening = None
                # delite tr from database
                tr.delete()
            
            sub.save()

            return redirect('client', id=client_id)
        
        if type == "group":
            col = int(data["col"])
            for _ in range(col):
                price = data["price"]
                way = "card"
                if data['role'] == "money":
                    way = "cash"
                if data['role'] == "site":
                    way = "site"

                date = datetime.date(*(map(int, data['date'].split('-'))))
                pay = Peyment(client=client, way=way, pay_type="group", group=None, date=date, value=price, zal=zal)
                pay.save()
                
                notpayd = SingleTren.objects.filter(client=client, pay__isnull=True, trening__trening_type='group').order_by('trening__day').first()
                if notpayd:
                    notpayd.pay = pay
                    notpayd.save()
                else:
                    sgtren = SingleTren(client=client, pay=pay, trening=None)
                    sgtren.save()
                
            return redirect('client', id=client_id)
        
        if type == "group_month":
            way = "card"
            if data['role'] == "money":
                way = "cash"
            if data['role'] == "site":
                way = "site"
            
            date = datetime.date(*(map(int, data['date'].split('-'))))
            pay = Peyment(client=client, way=way, pay_type="group_month", group=None, date=date, value=data['price'], zal=zal)
            pay.save()
            
            
            startdate = datetime.date(*(map(int, data['startdate'].split('-'))))
            enddate = datetime.date(*(map(int, data['enddate'].split('-'))))
            sub = Subscription(start_date=startdate, end_date=enddate, num_sessions=int(data['col']), client=client, pay=pay, sport_group=None, tren_type="group")
            sub.save()
            
            # get all SingeTren where client is client and pay is null and trening is not null and trening day >= startdate and trening day <= enddate and trening trening_type is group and trening group is group and order by trening day            
            sgtrs = SingleTren.objects.filter(client=client, pay__isnull=True, trening__isnull=False, trening__day__gte=startdate, trening__day__lte=enddate, trening__trening_type='group').order_by('trening__day')

            for tr in sgtrs:
                if sub.num_sessions <= 0:
                    break
                
                # add sub trenings tr trening and num sessions minus 1
                sub.trenings.add(tr.trening)
                sub.num_sessions -= 1
                
                tr.client = None
                tr.trening = None
                # delite tr from database
                tr.delete()
            
            sub.save()
            
            return redirect('client', id=client_id)

    percent = Param.objects.get(key="site_pay_percent")
    zals = list(Zal.objects.all())
    if type == "one":
        price = Param.objects.get(key="prise_one")

        return render(request=request, template_name="fitclub/new_pay.html", context={'zals': zals, 'client': client, 'type': type, 'price': price, 'percent': percent.value})
    
    if type == "one_month":
        price = Param.objects.get(key="price_one_month")

        return render(request=request, template_name="fitclub/new_pay.html", context={'zals': zals, 'client': client, 'type': type, 'price': price, 'percent': percent.value})
    
    if type == "group":
        price = Param.objects.get(key="price_group")

        return render(request=request, template_name="fitclub/new_pay.html", context={'zals': zals, 'client': client, 'type': type, 'price': price, 'groups': client.groups.all(), 'percent': percent.value})
    
    if type == "group_month":
        price = Param.objects.get(key="price_group_month")

        return render(request=request, template_name="fitclub/new_pay.html", context={'zals': zals, 'client': client, 'type': type, 'price': price, 'groups': client.groups.all(), 'percent': percent.value})

    if type.split('-')[0] == "massage":
        
        massage_type = MassageTypes.objects.get(pk=int(type.split('-')[1]))
        price = massage_type.prise

        title = "Массаж - " + massage_type.title

        return render(request=request, template_name="fitclub/new_pay.html", context={'zals': zals, 'title': title, 'mt': massage_type, 'client': client, 'type': 'massage', 'price': price, 'groups': client.groups.all(), 'percent': percent.value})


def allselary(request, type="all"):
    if not request.user.is_authenticated:
        return redirect('login')

    return redirect('selary', type="all")


def selary(request, type):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()

    rls = []
    if type == "all":
        rls = ['trener', 'admin', 'masager']
    else:
        rls = [type]


    users = User.objects.filter(
    groups__name__in=rls)
    
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

        
        if len(user.groups.all()) > 0:
            rl = user.groups.all()[0].name
        else:
            rl = "none" 
        
        if rl == "admin":
            usrs.append([user, gv, gv, 0])
        else:
            usrs.append([user, sm, gv, sma - allgv])
    
    mnth = month if len(str(month)) == 2 else "0" + str(month)
    return render(request=request, template_name="fitclub/selary.html", context={'users': usrs, 'ym': f"{year}-{mnth}", "type": type, "y": year, "m": month})


@csrf_exempt
def new_selary(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()
    userr = User.objects.get(pk=id)
    
    if request.method == "POST":
        data = request.POST
        col = data['col']
        
        zal = None
        if 'zal' in data:
            zal_pk = data['zal']
            if zal_pk != 'none':
                zal = Zal.objects.get(pk=int(zal_pk))
        
        selr = Salary(user=userr, date=datetime.date.today(), give=col, accure=-1, zal=zal)
        selr.save()  
        return redirect('selary')

    slrsum = None
    admsl = AdminSalary.objects.filter(user=userr).first()
    if admsl and admsl.type == "percent":
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
        groups__name__in=['trener', 'admin', 'masager'])
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
        
        prib = ins - (zp+spnd)
        
        slrsum = prib * admsl.value / 100

    
    zals = list(Zal.objects.all())
    return render(request=request, template_name="fitclub/newsalary.html", context={'zals': zals, 'user': userr, 'admsl': admsl, 'slrsum': slrsum})


def allprselary(request, month, year):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return redirect('prselary', type="all", month=month, year=year)



def prselary(request, type, month, year):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()

    rls = []
    if type == "all":
        rls = ['trener', 'admin', 'masager']
    else:
        rls = [type]

    users = User.objects.filter(
    groups__name__in=rls)
    
    if year == datetime.date.today().year and month == datetime.date.today().month:
        return redirect('selary', type=type)
    
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

        if len(user.groups.all()) > 0:
            rl = user.groups.all()[0].name
        else:
            rl = "none" 
        
        if rl == "admin":
            usrs.append([user, gv, gv])
        else:
            usrs.append([user, sm, gv])
    
    mnth = month if len(str(month)) == 2 else "0" + str(month)
    return render(request=request, template_name="fitclub/selary.html", context={'pr': True, 'users': usrs, 'ym': f"{year}-{mnth}", "type": type, "y": year, "m": month})


def dohod(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    zals = list(Zal.objects.all())
    
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
    groups__name__in=['trener', 'admin', 'masager'])
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
    
    return render(request=request, template_name="fitclub/dohod.html", context={'zals': zals, 'incomes': incomes, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': f"{year}-{month}", 'day': f"{year}-{month}-{day}", 'week': f"{year}-W{week}", 'month': f"{year}-{month}"})


def zdohod(request, z):
    if not request.user.is_authenticated:
        return redirect('login')
    zal = Zal.objects.filter(pk=z).first()
    
    zals = list(Zal.objects.all())
    
    year = datetime.date.today().year
    month = datetime.date.today().month
    day = datetime.date.today().day
    week = datetime.date.today().isocalendar().week
    
    ins = 0
    pays = Peyment.objects.filter(date__year=str(year), date__month=str(month), zal=zal)
    for p in pays:
        ins += p.value
    
    User = get_user_model()
    users = User.objects.filter(
    groups__name__in=['trener', 'admin', 'masager'])
    zp = 0
    for user in users:
        selrs = Salary.objects.filter(user=user, date__year=str(year), date__month=str(month), zal=zal)
        for sl in selrs:
            zp += sl.give
    
    spnd = 0
    spendings = Spending.objects.filter(date__year=str(year), date__month=str(month), zal=zal).order_by('-date')
    for s in spendings:
        spnd += s.value
    
    
    incomes = Income.objects.filter(date__year=str(year), date__month=str(month), zal=zal).order_by('-date')
    for inc in incomes:
        ins += inc.value
    
    return render(request=request, template_name="fitclub/dohod.html", context={'zal': zal,'zals': zals, 'zal_id': z,'incomes': incomes, 'ins': ins, 'outs': zp + spnd, 'prib': ins - (zp+spnd), 'zp': zp, 'spends': spendings, 'ym': f"{year}-{month}", 'day': f"{year}-{month}-{day}", 'week': f"{year}-W{week}", 'month': f"{year}-{month}"})


def prdohod(request, type, date):
    if not request.user.is_authenticated:
        return redirect('login')
    if type == "day":
        dt = datetime.date(*(map(int, date.split('-'))))
        ins = 0
        pays = Peyment.objects.filter(date=dt)
        for p in pays:
            ins += p.value
        
        User = get_user_model()
        users = User.objects.filter(
        groups__name__in=['trener', 'admin', 'masager'])
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
        groups__name__in=['trener', 'admin', 'masager'])
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
        groups__name__in=['trener', 'admin', 'masager'])
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
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        zal = None
        if 'zal' in data:
            zal_pk = data['zal']
            if zal_pk != 'none':
                zal = Zal.objects.get(pk=int(zal_pk))
        
        spend = Spending(key=data['name'], value=int(data['col']), spend_type="default", date=dt, zal=zal)
        spend.save()
        
        return redirect('dohod')

    td = datetime.date.today()
    zals = list(Zal.objects.all())
    return render(request=request, template_name="fitclub/newspend.html", context={'zals': zals, 'ym': td})


@csrf_exempt
def edit_spend(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
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
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        zal = None
        if 'zal' in data:
            zal_pk = data['zal']
            if zal_pk != 'none':
                zal = Zal.objects.get(pk=int(zal_pk))
        income = Income(key=data['name'], value=int(data['col']), date=dt, zal=zal)
        income.save()
        
        return redirect('dohod')

    td = datetime.date.today()
    
    zals = list(Zal.objects.all())

    return render(request=request, template_name="fitclub/newspend.html", context={'zals': zals, 'ym': td, 'inc': True})


@csrf_exempt
def edit_income(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    income = Income.objects.get(pk=id)
    if request.method == "POST":
        data = request.POST
        
        dt = datetime.date(*(map(int, data['date'].split('-'))))
        
        income.key=data['name']
        income.value=data['col']
        income.date=dt
        income.save()
        
        return redirect('dohod')

    return render(request=request, template_name="fitclub/editspend.html", context={'spend': income, 'inc': True})


@csrf_exempt
def new_client(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "POST":
        data = request.POST
        
        client = Client(name=data['name'], surname=data['surname'])
        if 'phone' in data:
            client.phone = data['phone']
        if 'email' in data:
            client.email = data['email']
        
        client.save()
        
        return redirect('clients')
    
    return render(request=request, template_name="fitclub/new_client.html", context={})


@csrf_exempt
def new_mas(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    User = get_user_model()
    client = Client.objects.get(pk=id)
    
    if request.method == "POST":
        data = request.POST
        mt = MassageTypes.objects.get(pk=data['mastype'])
        ts = datetime.time(*(map(int, data['starttime'].split(':'))))
        te = datetime.time(*(map(int, data['endtime'].split(':'))))

        dt = datetime.date(*(map(int, data['date'].split('-'))))

        trener = User.objects.get(pk=int(data['trener']))
        helper = None
        
        progul = False
        if "progul" in data:
            progul =  True

        col = 0 if progul else 1
        
        trening = Trening(start=ts, end=te, day=dt, group=None, trening_type=f"massage_{mt.pk}", col=col, is_was=True, progul=progul, trener=trener, helper=helper)
        trening.save()
        trening.clients.add(client)
        trening.save()

        sgt = Massage.objects.filter(client=client, trening__isnull=True, pay__pay_type=f'massage_{mt.pk}').order_by('pay__date').first()

        if sgt:
            sgt.trening = trening
            sgt.save()
        else:
            nsg = Massage(client=client, trening=trening, pay=None)
            nsg.save()
                
        return redirect('client', id=id)

    treniers = User.objects.filter(groups__name='masager')

    rl = ""
    if len(request.user.groups.all()) > 0:
        rl = request.user.groups.all()[0].name
    else:
        rl = "none"

    massage_types = MassageTypes.objects.all()

    return render(request=request, template_name="fitclub/new_per.html", context={'mt': massage_types, 'ismas': True, 'client': client, 'user': request.user, 'treniers': treniers, 'rl': rl})


@csrf_exempt
def chg_group(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    sub = Subscription.objects.get(pk=id)
    client = sub.client
    subtype = sub.tren_type
    
    if request.method == "POST":
        data = request.POST
        sub.start_date = datetime.date(*(map(int, data['startdate'].split('-'))))
        sub.end_date = datetime.date(*(map(int, data['enddate'].split('-'))))
        sub.num_sessions = int(data['col'])
        sub.save()

        return redirect('client', id=client.pk)

    return render(request=request, template_name="fitclub/chg_group.html", context={'sub': sub, 'client': client, 'type': subtype})


@csrf_exempt
def new_user(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        data = request.POST
        User = get_user_model()
        user = User.objects.create_user(data['login'], data['email'], data['password'])
        user.save()
        user.groups.add(Group.objects.get(name=data['role']))
        user.first_name = data['name']
        user.last_name = data['surname']
        user.save()
        return redirect('users')
    
    return render(request=request, template_name="fitclub/new_user.html", context={})


@csrf_exempt
def params(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        data = request.POST
        prms = Param.objects.all()
        for prm in prms:
            prm.value = data[f'param_{prm.pk}']
            prm.save()
        return redirect('params')


    params = Param.objects.all()
    return render(request=request, template_name="fitclub/params.html", context={'prms': params})

def massagetypes(request):
    if not request.user.is_authenticated:
        return redirect('login')

    types = MassageTypes.objects.all()
    return render(request=request, template_name="fitclub/massagetypes.html", context={'types': types})


@csrf_exempt
def mastpnew(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        data = request.POST
        tp = MassageTypes(title=data['title'], prise=data['prise'], trener_sum=data['trener_sum'])
        tp.save()
        return redirect('massagetypes')

    return render(request=request, template_name="fitclub/mastpnew.html", context={})


@csrf_exempt
def mastpedit(request, id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        data = request.POST
        tp = MassageTypes.objects.get(pk=id)
        tp.title = data['title']
        tp.prise = data['prise']
        tp.trener_sum = data['trener_sum']
        tp.save()
        return redirect('massagetypes')
    
    tp = MassageTypes.objects.get(pk=id)
    return render(request=request, template_name="fitclub/mastpedit.html", context={'tp': tp})


def guide(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request=request, template_name="fitclub/guide.html", context={})