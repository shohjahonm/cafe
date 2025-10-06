import os
import csv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, Poll
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

# Xabarlarni ishlovchi funksiya
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    if text == "📨 Shikoyat va takliflar":
        context.bot.send_message(chat_id=chat_id, text="Iltimos, shikoyat yoki taklifingizni yozing:")

    elif text == "📊 So‘rovnomada qatnashish":
        questions = [
            "Bot sizga yoqmoqdami?",
            "Xizmatdan mamnunmisiz?",
            "Qanday yaxshilash mumkin?"
        ]

        options = [
            ["Ha", "Yo‘q"],                     # 1-savol uchun javoblar
            ["Ha", "Yo‘q", "Qisman"],           # 2-savol uchun javoblar
            ["Ko‘proq variant", "Kamroq variant"]  # 3-savol uchun javoblar
        ]

        for i, question in enumerate(questions):
            context.bot.send_poll(
            chat_id=update.effective_chat.id,
            question=question,
            options=options[i],
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
