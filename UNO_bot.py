import telebot
from telebot import types

def get_token():
    with open('TOKEN.txt') as f:
        return f.readline()

bot = telebot.TeleBot(get_token())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Привет, как дела')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Не могу помочь, сорри')
    else:
        bot.send_message(message.from_user.id, 'хз')

def get_name(message):


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Ok')

bot.polling(none_stop=True, interval=2)

def main():
    ...
    # token = get_token()
    # bot = telebot.TeleBot(token)

if __name__ == '__main__':
    main()

