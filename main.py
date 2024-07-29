from flask import Flask
import telebot
import requests
from telebot import types

API_TOKEN = '7383759128:AAHuhFR4rgkRbxD7pSLLVRO-Sts5srcn9GU'  # Replace with your actual token
OWNER_ID = 6742022802  # Replace with your actual Telegram user ID
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running!'

@bot.message_handler(commands=['start'])
def start(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Get Access Token", url="https://github.com/settings/tokens")
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        'Welcome to Wevy Source 🌊\nPlease send me your personal GitHub access token.\n\n※ If you do not know how to get it, click the button below.',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, get_token)

def is_owner(message):
    return message.from_user.id == OWNER_ID

def get_token(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    user_data[message.chat.id] = {'token': message.text}
    bot.send_message(message.chat.id, 'Now, send me the new repository name.')
    bot.register_next_step_handler(message, get_repo_name)

def get_repo_name(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    user_data[message.chat.id]['repo_name'] = message.text
    bot.send_message(message.chat.id, 'Send me the repository description.')
    bot.register_next_step_handler(message, get_description)

def get_description(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    user_data[message.chat.id]['description'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Yes', 'No')
    bot.send_message(message.chat.id, 'Do you want the repository to be private? Send "Yes" or "No".', reply_markup=markup)
    bot.register_next_step_handler(message, get_privacy)

def get_privacy(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    user_data[message.chat.id]['private'] = message.text.lower() == 'yes'
    create_repo(message)

def create_repo(message):
    if not is_owner(message):
        bot.send_message(message.chat.id, 'Sorry, this bot is for the owner only.')
        return

    chat_id = message.chat.id

    repo_data = {
        "name": user_data[chat_id]['repo_name'],
        "description": user_data[chat_id]['description'],
        "private": user_data[chat_id]['private']
    }

    headers = {
        "Authorization": f"token {user_data[chat_id]['token']}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(
        "https://api.github.com/user/repos",
        json=repo_data,
        headers=headers
    )

    if response.status_code == 201:
        bot.send_message(chat_id, 'The repository has been successfully created!')
    else:
        bot.send_message(chat_id, f'Failed to create the repository. Status code: {response.status_code}')
        bot.send_message(chat_id, str(response.json()))

    user_data.pop(chat_id, None)

if __name__ == '__main__':
    bot.polling(none_stop=True)
    app.run(host='0.0.0.0', port=80)
  
