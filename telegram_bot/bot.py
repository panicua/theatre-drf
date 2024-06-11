from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
from decouple import config

# TELEGRAM_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
WEBSITE_BASE_URL = config("WEBSITE_BASE_URL")


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Genres", callback_data='genres')],
        [InlineKeyboardButton("Actors", callback_data='actors')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice == 'genres':
        response = requests.get(f'{WEBSITE_BASE_URL}/api/theatre/genres/')
        answer_string = ""
        for result in response.json()['results']:
            text = f"*id:* {result['id']}; *name:* {result['name']}"
            answer_string += f"{text}\n"
        await query.edit_message_text(text=f"{answer_string}", parse_mode="markdown")

    elif choice == 'actors':
        response = requests.get(f'{WEBSITE_BASE_URL}/api/theatre/actors/')
        answer_string = ""
        for result in response.json()['results']:
            text = f"*id:* {result['id']}; *full_name:* {result['full_name']}"
            answer_string += f"{text}\n"
        await query.edit_message_text(text=f"{answer_string}", parse_mode="markdown")


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == '__main__':
    main()
