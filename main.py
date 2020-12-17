import config
import telebot
import requests
from telebot import types
from bs4 import BeautifulSoup as BS

bot = telebot.TeleBot(config.token)

# Декодировать json
response = requests.get(config.url).json()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('Weather')
    itembtn2 = types.KeyboardButton('Exchange rates')
    markup.add(itembtn1, itembtn2)

    msg = bot.send_message(message.chat.id, "Select:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_select_step)


def process_select_step(message):
    try:
        if message.text == 'Exchange rates':
            coins(message)

        elif message.text == 'Weather':
            weather(message)
        else:
            send_welcome(message)

    except Exception:
        bot.reply_to(message, 'ooops!')


# Погода
def weather(message):
    global t_min, t_max, text
    r = requests.get('https://sinoptik.ua/погода-бишкек')
    html = BS(r.content, 'html.parser')

    for el in html.select('#content'):
        t_min = el.select('.temperature .min')[0].text
        t_max = el.select('.temperature .max')[0].text
        text = el.select('.wDescription .description')[0].text

    # убрать клавиатуру
    markup = types.ReplyKeyboardRemove(selective=False)

    bot.send_message(message.chat.id, "Hello!, weather for today:\n" +
                     t_min + ', ' + t_max + '\n' + text, reply_markup=markup)


# Курсы валют
def coins(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('USD')
    itembtn2 = types.KeyboardButton('EUR')
    itembtn3 = types.KeyboardButton('RUR')
    itembtn4 = types.KeyboardButton('KZT')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    msg = bot.send_message(message.chat.id,
                           "Find out the cash rate", reply_markup=markup)
    bot.register_next_step_handler(msg, process_coin_step)


def process_coin_step(message):
    try:
        # убрать клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        for coin in response:
            if message.text == coin['ccy']:
                bot.send_message(message.chat.id,
                                 printCoin(coin['buy'], coin['sale']),
                                 reply_markup=markup, parse_mode="Markdown")

    except Exception:
        bot.reply_to(message, 'ooops!')


def printCoin(buy, sale):
    """Вывод курса пользователю"""
    return ("💰 *Purchase rate:* " + str(buy) +
            "\n💰 *Selling rate:* " + str(sale))


bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)




