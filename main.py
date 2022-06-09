import datetime

import requests
import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import numpy as np
from bs4 import BeautifulSoup

reply_keyboard = [['/Dice', '/Scoreboard'], ['/Events', '/Daily']]
reply_keyboard2 = [['D6', '2D6', 'd20'], ['d20 2D4', 'd100', 'Назад']]
reply_scoreboard = []
players = dict()
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=False)


def close_keyboard(update, context):
    update.message.reply_text(
        reply_markup=ReplyKeyboardRemove()
    )


def dice(update, context):
    update.message.reply_text(
        "Для броска кубиков можно указать несколько наборов игральных костей через пробел:\n<Кол-во бросокв>D<Кол-во граней>\nНа клавиатуре доступны примеры ввода команды",
        reply_markup=markup2
    )


def daily(update, context):
    req = f"https://hobbygames.ru/"
    r = requests.get(req)
    html_text = r.text
    soup = BeautifulSoup(html_text, "html.parser")
    fnd = soup.find('div', {"class": "game-of-day__image"})

    link = fnd.find('a')
    name = fnd.find('img')

    fnd = soup.find('div', {"class": "row game-of-day__bottom"})
    price = fnd.find('span', {"class": "price"}).get_text()
    res = ""

    for c in price:
        if c in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            res += c
    res += '₽'

    update.message.reply_text(
        name.get("alt") + '\n' + res + '\n' + link.get("href")
        )


def update_players():
    power = 2
    while pow(power, 2) < len(players):
        power += 1
    counter = 0

    reply_scoreboard.clear()
    reply_scoreboard.append([])
    for key in players.keys():
        reply_scoreboard[counter].append(str(key) + ": " + str(players[key]))

        if len(reply_scoreboard[counter]) == power:
            reply_scoreboard.append([])
            counter += 1


def tg_start(update, context):
    update.message.reply_text(
        "Я бот-помощник для настольных игр. Я могу бросать кости, считать очки, создавать мероприятия на карте и показывать игру дня с сайта hobbygames.ru",
        reply_markup=markup
    )
    players.clear()
    update_players()


def scoreboard(update, context):
    if len(context.args) == 0:
        markup_scoreboard = ReplyKeyboardMarkup(reply_scoreboard, one_time_keyboard=False)
        update.message.reply_text(
            "Счётчик очков\n/Scoreboard можно заменить короткой версией /s\nДля добавления нового игрока /s new <Имя игрока>\nДля добавления очков /s + <Очки> <Имя игрока>\nДля установки конкретного кол-ва очков /s = <Очки> <Имя игрока>\nДля удаления игрока /s remove <Имя игрока>\nЕсли не указывать имя игрока, то очки будут добавлены/установлены у всех игроков\n\nДля сохранения результатов /s save <Название игры>\nНазвание игры вводить не обязяательно",
            reply_markup=markup_scoreboard
        )
    else:
        if context.args[0] == "save":
            timenow = str(datetime.datetime.now())[:-7]
            timenow = timenow.replace(':', '-')
            f = open(timenow + ".txt", 'w+')
            if len(context.args) >= 2:
                for i in range(1, len(context.args)):
                    f.writelines(context.args[i] + ' ')
                f.writelines('\n')
            f.writelines(timenow + '\n')
            f.close()

            for key in players.keys():
                f.writelines(key + ': ' + str(players[key]) + '\n')
        elif context.args[0] == "new" and len(context.args) >= 2:
            players.update({context.args[1]: 0})
        elif context.args[0] == "remove":
            if len(context.args) >= 2:
                players.pop(context.args[1])
            else:
                players.clear()
        elif context.args[0] == "+":
            if len(context.args) >= 3:
                players[context.args[2]] = str(int(players[context.args[2]]) + int(context.args[1]))
            elif len(context.args) == 2:
                for key in players.keys():
                    players[key] = str(int(players[key]) + int(context.args[1]))
        elif context.args[0] == "=":
            if len(context.args) >= 3:
                players[context.args[2]] = context.args[1]
            elif len(context.args) == 2:
                for key in players.keys():
                    players[key] = context.args[1]

        update_players()

        markup_scoreboard = ReplyKeyboardMarkup(reply_scoreboard, one_time_keyboard=False)
        update.message.reply_text(
            "Успешно",
            reply_markup=markup_scoreboard
        )




def echo(update, context):
    text = str(update.message.text)
    if 'назад' in text.lower():
        update.message.reply_text(
            "Чем я могу помочь?",
            reply_markup=markup
        )
    elif 'D' in text.upper():
        res = str()
        intres = 0
        throws = 0

        calls = text.upper().split(sep=' ')
        for i in calls:
            dpos = i.upper().find('D')
            quantity = 1
            if dpos > 0:
                quantity = int(i[0:dpos])

            dicetype = int(i[dpos + 1:])

            while quantity > 0:
                throws += 1
                roll = np.random.randint(1, dicetype + 1)
                intres += roll
                if throws > 1:
                    res += "+ "
                res += str(roll) + ' '
                quantity -= 1

        if throws == 1:
            update.message.reply_text("Результат броска: " + res)
        else:
            update.message.reply_text("Результат броска: " + res + "= " + str(intres))


def main():
    updater = Updater("5335234442:AAGMABLSsEPpeTn22wYyKtLRYE6jNYr0ZaU", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", tg_start))
    dp.add_handler(CommandHandler("close", close_keyboard))

    dp.add_handler(CommandHandler("Dice", dice))
    dp.add_handler(CommandHandler("Daily", daily))
    dp.add_handler(CommandHandler("Scoreboard", scoreboard))
    dp.add_handler(CommandHandler("s", scoreboard))

    text_handler = MessageHandler(Filters.text, echo)

    dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()