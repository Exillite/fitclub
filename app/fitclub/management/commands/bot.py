from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot
from fitclub.models import Client
from app.settings import TG_TOKEN


# Объявление переменной бота
bot = TeleBot(TG_TOKEN, threaded=False)


@bot.message_handler(commands=['start', 'help', 'reg'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, "Введите код:")
    bot.register_next_step_handler(msg, regtg)

def regtg(message):
    const = 4564
    dt = message.text
    # check is dt number
    if dt.isdigit():
        dt = int(dt)
        clid = dt - const
        cl = Client.objects.filter(id=clid).first()
        if cl:
            cl.tg = message.chat.id
            cl.save()
            bot.send_message(message.chat.id, "Telegram аккаунт успешно привязан!🎉")
        else:
            bot.send_message(message.chat.id, "Неверный код!")
    else:
        bot.send_message(message.chat.id, "Неверный код!")

def send_message(chat_id, text):
    bot.send_message(int(chat_id), text)



# Название класса обязательно - "Command"
class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()								# Загрузка обработчиков
        bot.infinity_polling()