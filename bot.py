import os
import csv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PollAnswerHandler

# Environment variables
TOKEN = os.getenv("TOKEN", "8328899370:AAEZCpFklna6jVgCNC6VCeFGp_VYj7Dx4hA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1139713731"))

# /start komandasi
def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("📨 Shikoyat va takliflar"), KeyboardButton("📊 So‘rovnomada qatnashish")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Salom! 👋\nAristocrat Cafe botiga xush kelibsiz.\nQuyidagi menyudan tanlang:", 
        reply_markup=reply_markup
    )

# So‘rovnoma ma’lumotlari
SURVEY_QUESTIONS = [
    "Sizga qaysi ovqatlar yoqadi?",
    "Sizga qaysi Fri-setlar yoqadi?",
    "Sizga oshxonadagi qaysi qulayliklar yoqadi?",
    "Oshxonamizni 1-5 gacha baholang"
]

SURVEY_OPTIONS = [
    ["Manti", "Tovuq Kabob", "Grechka", "Osh", "Lag'mon", "Galupsi"],
    ["Fri", "Fri Kolbasa", "Fri Sosiska", "Fri Chicken"],
    ["Tozalik", "Ovqatlarning ta'mi va sifati", "Xodimlarning muomalasi"],
    ["1", "2", "3", "4", "5"]
]

# Xabarlarni ishlovchi funksiya
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == "📨 Shikoyat va takliflar":
        context.bot.send_message(chat_id=chat_id, text="Iltimos, shikoyat yoki taklifingizni yozing:")

    elif text == "📊 So‘rovnomada qatnashish":
        # Foydalanuvchi uchun indeksni 0 ga o‘rnatamiz
        context.user_data['survey_index'] = 0
        context.user_data['chat_id'] = chat_id

        # Birinchi so‘rovnomani yuboramiz
        context.bot.send_poll(
            chat_id=chat_id,
            question=SURVEY_QUESTIONS[0],
            options=SURVEY_OPTIONS[0],
            is_anonymous=False,
            allows_multiple_answers=True
        )

    else:
        # Talab/taklifni adminga yuborish
        context.bot.send_message(chat_id=ADMIN_ID, text=f"Yangi talab/taklif:\n\n{text}")
        context.bot.send_message(chat_id=chat_id, text="Fikringiz uchun rahmat! Bu biz uchun juda ham muhim!! ✅")

        # CSV-ga yozish
        with open("results.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([chat_id, text])

# So‘rovnoma javoblarini qayta ishlash
def handle_poll_answer(update: Update, context: CallbackContext):
    poll_answer = update.poll_answer
    user_id = poll_answer.user.id
    options_ids = poll_answer.option_ids

    # Adminga yuborish
    context.bot.send_message(chat_id=ADMIN_ID, text=f"Foydalanuvchi {user_id} so‘rovnomaga javob berdi: {options_ids}")

    # CSV-ga yozish
    with open("results.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, options_ids])

    # Foydalanuvchi chat_id ni olish
    chat_id = context.user_data.get('chat_id')
    if not chat_id:
        chat_id = user_id  # fallback

    # Keyingi savolni yuborish
    survey_index = context.user_data.get('survey_index', 0) + 1
    context.user_data['survey_index'] = survey_index

    if survey_index < len(SURVEY_QUESTIONS):
        context.bot.send_poll(
            chat_id=chat_id,
            question=SURVEY_QUESTIONS[survey_index],
            options=SURVEY_OPTIONS[survey_index],
            is_anonymous=False,
            allows_multiple_answers=True
        )
    else:
        # Tugaganda rahmat xabarini yuboramiz
        keyboard = [
            [KeyboardButton("📨 Shikoyat va takliflar"), KeyboardButton("📊 So‘rovnomada qatnashish")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat_id,
            text="✅ So'rovnomada qatnashganingiz uchun rahmat!\nSizning fikringiz biz uchun muhim!",
            reply_markup=reply_markup
        )
        context.user_data.clear()

# Main
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(PollAnswerHandler(handle_poll_answer))

    updater.start_polling()
    print("Bot ishlayapti...")
    updater.idle()

if __name__ == "__main__":
    main()
