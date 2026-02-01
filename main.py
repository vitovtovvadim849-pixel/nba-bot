import requests
import telebot
from telebot import types
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


# ===== КНОПКИ =====
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.add("🔮 Прогноз", "📅 Матчи")
    kb.add("📊 Статистика", "ℹ️ Помощь")

    return kb


# ===== ДАННЫЕ =====
def last_games(team_id, n=5):

    url = f"https://www.balldontlie.io/api/v1/games?team_ids[]={team_id}&per_page={n}"

    return requests.get(url).json()["data"]


def team_stats(team_id):

    games = last_games(team_id)

    scored = conceded = 0

    for g in games:

        if g["home_team"]["id"] == team_id:
            scored += g["home_team_score"]
            conceded += g["visitor_team_score"]
        else:
            scored += g["visitor_team_score"]
            conceded += g["home_team_score"]

    if len(games) == 0:
        return 110, 110

    return scored/len(games), conceded/len(games)


# ===== СТАРТ =====
@bot.message_handler(commands=['start'])
def start(m):

    bot.send_message(
        m.chat.id,
        "🏀 NBA Аналитик Бот\n\nВыбери действие:",
        reply_markup=main_menu()
    )


# ===== МАТЧИ =====
@bot.message_handler(func=lambda m: "Матчи" in m.text)
def games(m):

    url = "https://www.balldontlie.io/api/v1/games?per_page=5"

    data = requests.get(url).json()["data"]

    txt = "📅 Ближайшие матчи:\n\n"

    for g in data:
        txt += f"{g['home_team']['full_name']} — {g['visitor_team']['full_name']}\n"

    bot.send_message(m.chat.id, txt)


# ===== ПРОГНОЗ =====
@bot.message_handler(func=lambda m: "Прогноз" in m.text)
def predict(m):

    url = "https://www.balldontlie.io/api/v1/games?per_page=20"

    game = requests.get(url).json()["data"][0]

    home = game["home_team"]
    away = game["visitor_team"]

    h_sc, h_con = team_stats(home["id"])
    a_sc, a_con = team_stats(away["id"])

    home_pts = (h_sc + a_con)/2
    away_pts = (a_sc + h_con)/2

    total = home_pts + away_pts
    diff = home_pts - away_pts


    txt = f"""
🏀 Прогноз на матч

🏆 {home['full_name']} — {away['full_name']}

📈 Победа: {"Хозяева" if diff>0 else "Гости"}

📊 Счёт: {round(home_pts)}:{round(away_pts)}

🔥 Тотал: {round(total,1)}

🎯 Фора: {round(diff,1)}

📉 ТБ/ТМ 220.5: {"ТБ" if total>220.5 else "ТМ"}
"""

    bot.send_message(m.chat.id, txt)


# ===== СТАТА =====
@bot.message_handler(func=lambda m: "Статистика" in m.text)
def stats(m):

    bot.send_message(
        m.chat.id,
        "📊 Основано на последних 5 играх команд NBA"
    )


# ===== ПОМОЩЬ =====
@bot.message_handler(func=lambda m: "Помощь" in m.text)
def help(m):

    bot.send_message(
        m.chat.id,
        "🤖 Бот считает прогнозы по статистике\n"
        "Используй для тестов"
    )


bot.polling()
