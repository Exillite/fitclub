from app.celery import app
from .models import *
from .management.commands.bot import send_message

@app.task
def testshd():
    print("AAAAAAAAAAAAAAAAAAAAAAAAA OKOKOKOKOK")
    return 10

@app.task
def alert_subs(tren_id, isrn):
    tren = Trening.objects.get(pk=tren_id)
    for cl in tren.clients.all():

        # get if exists sub with this tren and client
        sub = Subscription.objects.filter(client=cl, trenings__id=tren_id).first()
        if sub:
            if sub.num_sessions == 0:
                if sub.tren_type == "group":
                    send_message(cl.tg, f"У вас закончился абонимент на групповые занятия!")
                else:
                    send_message(cl.tg, f"У вас закончился абонимент на индивидуальные занятия!")
