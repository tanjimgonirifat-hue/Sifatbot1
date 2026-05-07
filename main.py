import telebot
import pyotp
import requests
import random
import time
import os
import threading
from flask import Flask
from faker import Faker
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ কনফিগারেশন ---
TOKEN = '8783194900:AAH__MsqIgqwKn_-Pzg2NdxQsIJ1OjvAVY8' 
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwsevBN0x4ApVe17lnwiIZEpUE9kS6HkNrKMxSZKx10l6J4ng5wpS7FRVyODOQVPS-uJw/exec"
ADMIN_ID = 8061525743 
BOT_NAME = "𝐓𝐚𝐧𝐣𝐢𝐦 𝐀𝐮𝐭𝐨𝐦𝐚𝐭𝐢𝐨𝐧"

bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=20)
app = Flask(__name__)
fake = Faker()
executor = ThreadPoolExecutor(max_workers=15)

user_tasks = {}

@app.route('/')
def home():
    return f"🚀 {BOT_NAME} System is Live!"

def send_to_sheet(row):
    try:
        requests.post(WEB_APP_URL, json={"row": row}, headers={"Content-Type": "application/json"}, timeout=15)
    except:
        pass

# --- 🎨 স্টাইলিশ কিবোর্ড ---
def main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('🚀 𝐒𝐭𝐚𝐫𝐭 𝐖𝐨𝐫𝐤'))
    markup.add(
        telebot.types.KeyboardButton('👤 𝐌𝐲 𝐏𝐫𝐨𝐟𝐢𝐥𝐞'), 
        telebot.types.KeyboardButton('💸 𝐖𝐢𝐭𝐡𝐝𝐫𝐚𝐰'), 
        telebot.types.KeyboardButton('👥 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥')
    )
    markup.add(telebot.types.KeyboardButton('📞 𝐒𝐮𝐩𝐩𝐨𝐫𝐭'))
    if user_id == ADMIN_ID:
        markup.add(telebot.types.KeyboardButton('⚙️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐧𝐭𝐫𝐨𝐥'))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        f"🌟 **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 {BOT_NAME}** 🌟\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👋 Hello! Earn money by completing simple tasks.\n"
        "⚡ **Fast Submission | Auto Review | 24/7 Pay**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👇 Use the menu below to start!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(message.from_user.id), parse_mode="Markdown")

# --- 📋 টাস্ক লজিক ---
@bot.message_handler(func=lambda message: message.text == "🚀 𝐒𝐭𝐚𝐫𝐭 𝐖𝐨𝐫𝐤")
def show_tasks(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📱 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 + 𝟐𝐅𝐀 ⇛ $𝟎.𝟎𝟏𝟕𝟎", callback_data="task_inst"))
    bot.send_message(message.chat.id, "✨ **𝐒𝐞𝐥𝐞𝐜𝐭 𝐘𝐨𝐮𝐫 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐓𝐚𝐬𝐤**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "task_inst")
def start_task(call):
    f_name = f"{fake.first_name()} {fake.last_name()}"
    login = f"{fake.user_name()}{random.randint(10, 99)}"
    pwd = fake.password(length=10)
    user_tasks[call.message.chat.id] = {"name": f_name, "login": login, "pass": pwd, "start_time": time.time()}
    
    task_info = (
        "📝 **𝐍𝐞𝐰 𝐓𝐚𝐬𝐤 𝐀𝐬𝐬𝐢𝐠𝐧𝐞𝐝**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 **𝐍𝐚𝐦𝐞:** `{f_name}`\n"
        f"📧 **𝐋𝐨𝐠𝐢𝐧:** `{login}`\n"
        f"🔑 **𝐏𝐚𝐬𝐬:** `{pwd}`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⏳ **Time Left:** 4 Minutes\n"
        "👉 Please send your **2FA Key** now."
    )
    bot.send_message(call.message.chat.id, task_info, parse_mode="Markdown")
    bot.register_next_step_handler(call.message, get_otp)

def get_otp(message):
    chat_id = message.chat.id
    if message.text and (message.text.startswith('/') or len(message.text) > 50): return
    
    # ৪ মিনিট টাইম-আউট চেক
    if chat_id in user_tasks and (time.time() - user_tasks[chat_id]['start_time'] > 240):
        bot.send_message(chat_id, "⏰ **Time's up! Task cancelled.**")
        user_tasks.pop(chat_id, None)
        return

    key = message.text.replace(" ", "")
    try:
        totp = pyotp.TOTP(key)
        otp = totp.now()
        user_tasks[chat_id]['2fa_key'] = key
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📤 𝐒𝐮𝐛𝐦𝐢𝐭 𝐑𝐞𝐩𝐨𝐫𝐭", callback_data="final_submit"))
        bot.send_message(chat_id, f"🔢 **𝐘𝐨𝐮𝐫 𝐎𝐓𝐏 𝐢𝐬:** `{otp}`\n\n✅ Click submit if ready!", reply_markup=markup, parse_mode="Markdown")
    except:
        bot.send_message(chat_id, "❌ **𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝟐𝐅𝐀 𝐊𝐞𝐲!** Try again.")
        bot.register_next_step_handler(message, get_otp)

@bot.callback_query_handler(func=lambda call: call.data == "final_submit")
def submit_data(call):
    chat_id = call.message.chat.id
    data = user_tasks.get(chat_id)
    if data:
        user_tasks[chat_id]['completed'] = True
        row = [time.ctime(), str(chat_id), data['name'], data['login'], data['pass'], data.get('2fa_key', 'N/A'), "Pending"]
        executor.submit(send_to_sheet, row)
        bot.edit_message_text("🚀 **𝐑𝐞𝐩𝐨𝐫𝐭 𝐒𝐮𝐛𝐦𝐢𝐭𝐭𝐞𝐝!**\nAdmin will review it soon. ✅", chat_id, call.message.message_id, parse_mode="Markdown")
        user_tasks.pop(chat_id, None)

@bot.message_handler(func=lambda message: message.text == "⚙️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐧𝐭𝐫𝐨𝐥" and message.from_user.id == ADMIN_ID)
def admin_panel(message):
    bot.send_message(message.chat.id, "🛠 **𝐃𝐚𝐬𝐡𝐛𝐨𝐚𝐫𝐝 𝐀𝐜𝐭𝐢𝐯𝐞**\nType 'Approved' in sheet status to notify users.")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
