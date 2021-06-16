import telebot
from telebot import types
from selenium import webdriver
import pandas as pd
import requests      # Библиотека для отправки запросов
import numpy as np   # Библиотека для матриц, векторов и линала
import pandas as pd  # Библиотека для табличек
import time
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
from fake_useragent import UserAgent
from collections import defaultdict
# подключим токен нашего бота
bot = telebot.TeleBot("1853816199:AAG3kq86wrXqL8MPHKmobzFLcVbzU47NBII")
# напишем, что делать нашему боту при команде старт
@bot.message_handler(func=lambda message: message.text == "go")
def keyboard_country(message, text="Привет, выберите страну, на бирже которой котируется акция."):

    try:
        #share_number = int(message.text)
        if message.text == 'go' or message.text == 'Поменять страну':
            keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
            itembtn1 = types.KeyboardButton('Россия')
            itembtn2 = types.KeyboardButton('Великобритания')
            itembtn3 = types.KeyboardButton('США')
            itembtn4 = types.KeyboardButton('Германия')
            itembtn5 = types.KeyboardButton('Франция')
            itembtn6 = types.KeyboardButton('Япония')# создадим кнопку
            keyboard.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6) # добавим кнопки 1 и 2 на первый ряд
            ans = bot.send_message(message.from_user.id, text= text, reply_markup= keyboard)
            # отправим этот вариант в функцию, которая его обработает

            bot.register_next_step_handler(ans, all_worker)
            print(ans.text)
        elif message.text:
            keyboard = types.ReplyKeyboardMarkup()  # наша клавиатура
            itembtn1 = types.KeyboardButton('Текущая цена')
            itembtn2 = types.KeyboardButton('Максимальная цена за сегодня')
            itembtn3 = types.KeyboardButton('Минимальная цена за сегодня')
            itembtn4 = types.KeyboardButton('Изменение в базисных пунктах')
            itembtn5 = types.KeyboardButton('Изменение в процентах')
            itembtn6 = types.KeyboardButton('Объем торгов')
            itembtn7 = types.KeyboardButton('Графики')
            itembtn8 = types.KeyboardButton('Поменять страну')# создадим кнопку
            keyboard.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6,itembtn7,itembtn8)
            current_share = message
            ans = bot.send_message(message.from_user.id, text=text, reply_markup=keyboard)
            print(ans)
            if ans.text != 'Поменять страну':
                # отправим этот вариант в функцию, которая его обработает
                bot.register_next_step_handler(ans, all_worker1, current_share)
                print(ans.text)
            elif ans.text == 'Поменять страну':
                text = 'Выберите интересующую страну'
                keyboard_country(ans, text)
    except:
        print('error')


#Кнопка списка акций, 2 этап
def new_keyboard(message):
    text = 'Пожалуйста, введите номер акции из списка'
    keyboard = types.ReplyKeyboardMarkup()
    itembtn = types.KeyboardButton('Список акций')  # создадим кнопку
    keyboard.add(itembtn)
    ans = bot.send_message(message.from_user.id, text= text, reply_markup= keyboard )
    bot.register_next_step_handler(ans, all_worker)

#Кнопки выбора для показателей или графиков, 3 этап
def indicators_grapichs(ans):
    text = 'Пожалуйста, выберите, какие данные желаете изучить'
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
    itembtn1 = types.KeyboardButton('Торговые показатели за сегодня')
    itembtn2 = types.KeyboardButton('Графики')
    keyboard.add(itembtn1, itembtn2)
    current_share = ans
    ans=bot.send_message(ans.from_user.id, text=text, reply_markup=keyboard)
    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(ans, all_worker1, current_share)
#Несколько кнопок с показателями
def data_one_share(ans, current_share):
    text = 'Пожалуйста, выберите интересующий показатель'
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
    itembtn1 = types.KeyboardButton('Текущая цена')
    itembtn2 = types.KeyboardButton('Максимальная цена за сегодня')
    itembtn3 = types.KeyboardButton('Минимальная цена за сегодня')
    itembtn4 = types.KeyboardButton('Изменение в базисных пунктах')
    itembtn5 = types.KeyboardButton('Изменение в процентах')
    itembtn6 = types.KeyboardButton('Объем торгов')  # создадим кнопку
    keyboard.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    ans = bot.send_message(ans.from_user.id, text= text, reply_markup=keyboard)
    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(ans, all_worker1, current_share)

#Поиск показателя для акции
def find_indicator(ans , current_share):
    try:
        text = 'Что еще хотитие узнать?'
        df = pd.read_csv('Shares.csv', delimiter='w')
        value = df.loc[int(current_share.text) - 1, f'{ans.text}']
        ans = bot.send_message(ans.from_user.id, value)
        keyboard_country(current_share, text)
        #bot.register_next_step_handler(ans, data_one_share, current_share, text)
    except:
        bot.send_message(ans.chat.id, 'Ошибка сбора данных')
        #keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")

def country_parser(ans):
    parsing_dict = {'Россия': 'russia', 'Великобритания': 'united-kingdom', 'США': 'united-states', 'Германия': 'germany',
                    'Франция': 'france', 'Япония': 'japan'}
    for country in parsing_dict:
        if country == ans.text:
            url = f'https://ru.investing.com/equities/{parsing_dict[country]}'
    response = requests.get(url, headers={'User-Agent': UserAgent().chrome})
    tree = response.content
    df = pd.read_html(tree)
    df = df[0]
    df = df.drop(['Unnamed: 0'], axis=1)
    df = df.drop(['Unnamed: 9'], axis=1)
    columns_names = ['Название компании', 'Текущая цена', 'Максимальная цена за сегодня',
                     'Минимальная цена за сегодня',
                     'Изменение в базисных пунктах', 'Изменение в процентах', 'Объем торгов', 'Время']
    df.columns = columns_names
    df.to_csv('Shares.csv', 'w', index=False, index_label=False)


#Функция для вывода списком
def get_tickers_string(companies_names):
    companies_str = []
    for val in list(enumerate(companies_names)):
        companies_str.append(str(val[0] + 1) + ') ' + val[1] + '\n')
    return ''.join(companies_str)

#Вывод списка акций
def share_worker(ans):
    if ans.text == 'Список акций':
       try:
           df = pd.read_csv('Shares.csv', delimiter='w')
           companies_names = []
           for name in df['Название компании']:
               companies_names.append(name)
           shares = get_tickers_string(companies_names)
           ans = bot.send_message(ans.chat.id, shares)
           bot.register_next_step_handler(ans, all_worker)
       except:
           bot.send_message(ans.chat.id, 'Ошибка системы')
           keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")
    else:
        bot.register_next_step_handler(ans, all_worker)


def all_worker(ans):
    countries = ["Россия", "Великобритания","США", 'Германия', 'Франция', 'Япония']

    if ans.text in countries:
        try:
            country_parser(ans)
            new_keyboard(ans)
        except:
            print(ans.text)
            #bot.send_message(ans.chat.id, 'Ошибка системы')
            #keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")

    elif ans.text == 'Список акций':
        try:
            share_worker(ans)
        except:
            bot.send_message(ans.chat.id, 'Ошибка системы')
            keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")

    elif ans.text.isdigit() == True:
        try:
            indicators_grapichs(ans)
        except:
            bot.send_message(ans.chat.id, 'Ошибка системы')
            keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")

#Фукнция для поиска данных по одной акции
def all_worker1(ans, current_share):
    financial_indicators = ['Текущая цена', 'Максимальная цена за сегодня', 'Минимальная цена за сегодня',
                            'Изменение в базисных пунктах', 'Изменение в процентах', 'Объем торгов']
    if ans.text in financial_indicators:
        try:
            find_indicator(ans, current_share)
        except:
            bot.send_message(ans.chat.id, 'Ошибка системы')
            keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")
    elif ans.text == "Торговые показатели за сегодня":
        try:
            data_one_share(ans, current_share)
        except:
            bot.send_message(ans.chat.id, 'Ошибка системы')
            keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")
    elif ans.text == "Графики":
        try:
            country_parser(ans)
        except:
            bot.send_message(ans.chat.id, 'Ошибка системы')
            keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")
    else:
        print('here', ans.text)
        bot.send_message(ans.chat.id, '1')
        #keyboard_country(ans, "Пожалуйста, попробуйте обратиться ко мне снова")






bot.polling(none_stop=True)

print(df)























