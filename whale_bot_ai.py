import telebot
from telebot import types
from config import TELEGRAM_TOKEN, PRICING, WELCOME_MESSAGE, ADMIN_ID, USDT_WALLET_ADDRESS
from datetime import datetime, timedelta

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_subscriptions = {}  # user_id: expiry_datetime

def is_subscribed(user_id):
    if user_id == ADMIN_ID:
        return True
    expiry = user_subscriptions.get(user_id)
    return expiry and datetime.now() < expiry

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📡 سیگنال", "💳 خرید اشتراک", "🆔 آیدی ادمین")
    bot.send_message(message.chat.id, WELCOME_MESSAGE, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda msg: msg.text == "💳 خرید اشتراک")
def show_subscription_options(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("ماهانه", "شش ماهه", "سالانه")
    bot.send_message(message.chat.id, "لطفا نوع اشتراک را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ["ماهانه", "شش ماهه", "سالانه"])
def handle_subscription_selection(message):
    duration_map = {
        "ماهانه": "monthly",
        "شش ماهه": "6months",
        "سالانه": "yearly"
    }
    key = duration_map[message.text]
    price = PRICING[key]["amount"]
    bot.send_message(message.chat.id, f"هزینه اشتراک {price} تتر می‌باشد.\nلطفاً مبلغ را به آدرس زیر پرداخت کرده و رسید را برای ادمین ارسال نمایید:\n\n`{USDT_WALLET_ADDRESS}`", parse_mode='Markdown')

@bot.message_handler(func=lambda msg: msg.text == "📡 سیگنال")
def signal_menu(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "❌ شما اشتراک فعالی ندارید. لطفاً از گزینه خرید اشتراک استفاده کنید.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("هوشمند", "دستی")
    bot.send_message(message.chat.id, "لطفاً نوع دریافت سیگنال را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "هوشمند")
def smart_signal(message):
    bot.send_message(message.chat.id,
                     "Gold BUY\nENTRY: 3326-3321\nSL: 3319\nTP1: 3328\nTP2: 3332\nTP3: 3333\nLeverage: 10x")

@bot.message_handler(func=lambda msg: msg.text == "دستی")
def ask_symbol(message):
    msg = bot.send_message(message.chat.id, "نام ارز مورد نظر را وارد کنید (مثلاً BTC):")
    bot.register_next_step_handler(msg, send_manual_signal)

def send_manual_signal(message):
    symbol = message.text.upper()
    signal = f"{symbol} BUY\nENTRY: قیمت مناسب فعلی\nSL: پشتیبانی نزدیک\nTP1: مقاومت اول\nTP2: مقاومت دوم\nTP3: مقاومت سوم\nLeverage: 5x"
    bot.send_message(message.chat.id, signal)

@bot.message_handler(func=lambda msg: msg.text == "🆔 آیدی ادمین")
def show_admin_id(message):
    bot.send_message(message.chat.id, f"آیدی ادمین برای ارسال رسید: {ADMIN_ID}", parse_mode='Markdown')

@bot.message_handler(commands=['activate'])
def activate_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id, days = message.text.split()
        user_subscriptions[int(user_id)] = datetime.now() + timedelta(days=int(days))
        bot.send_message(message.chat.id, f"اشتراک کاربر {user_id} برای {days} روز فعال شد.")
    except:
        bot.send_message(message.chat.id, "فرمت اشتباه. استفاده از دستور:\n/activate <user_id> <days>")

print("ربات فعال است...")
bot.infinity_polling()
