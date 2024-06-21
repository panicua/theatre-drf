import requests
from decouple import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
)

TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
WEBSITE_BASE_URL = config("WEBSITE_BASE_URL")


async def start(update: Update, context: CallbackContext) -> None:
    reply_markup = create_reply_markup()
    await update.message.reply_text(
        "Please choose:", reply_markup=reply_markup
    )


def create_reply_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Genres", callback_data="genres")],
        [InlineKeyboardButton("Actors", callback_data="actors")],
    ]
    return InlineKeyboardMarkup(keyboard)


def fetch_data(endpoint: str) -> str:
    response = requests.get(f"{WEBSITE_BASE_URL}/api/theatre/{endpoint}/")
    answer_string = text = ""
    for result in response.json()["results"]:
        if endpoint == "genres":
            text = f"*name:* {result['name']}"
        elif endpoint == "actors":
            text = f"*full_name:* {result['full_name']}"
        answer_string += f"{text}\n"
    return answer_string


async def handle_response(query, endpoint: str) -> None:
    try:
        answer_string = fetch_data(endpoint)
        await query.edit_message_text(
            text=answer_string, parse_mode="markdown"
        )
    except Exception as e:
        await query.edit_message_text(text=str(e))


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    choice = query.data
    if choice in ["genres", "actors"]:
        await handle_response(query, choice)

    reply_markup = create_reply_markup()
    await query.message.edit_reply_markup(reply_markup)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


if __name__ == "__main__":
    main()
