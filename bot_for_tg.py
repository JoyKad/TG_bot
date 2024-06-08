import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ApplicationBuilder,
)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
CREDENTIALS_FILE = '...' #Replace with a key file
SPREADSHEET_ID = '...' #Replace with the ID of your table
BOT_TOKEN = '...' #Replace with your bot token

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPE
)
authed_session = AuthorizedSession(credentials)
client = gspread.authorize(credentials=credentials)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1


async def start(update, context):
    await update.message.reply_text(
        "Привет!\n" "Если ты студент ... и ты хочешь узнать свою посещаемость, то отправьте команду /zachotka и ваш номер зачетной книжки (7 цифр).\n"
        "Например: /zachotka 1234567"
    )


async def get_attendance(update, context):
    user_id = update.message.from_user.id
    message_text = update.message.text

    try:
        zachotka_number = message_text.split(" ")[1]

        if len(zachotka_number) != 7 or not zachotka_number.isdigit():
            raise ValueError

        data = sheet.get_all_values()
        for row in data[1:]:

            if row[2] == str(zachotka_number):  
                name = row[0]
                attendance = float(row[1].replace(",", "."))

                if attendance >= 60:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Привет, {name}! Твоя посещаемость: {attendance}%.\n" "Молодец, продолжай в том же духе ходить на пары!",
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Привет, {name}! Твоя посещаемость: {attendance}%.\n" "Тебе следует не пропускать пары, или получишь выговор!",
                    )
                return


        await context.bot.send_message(
            chat_id=user_id,
            text="Студент с таким номером зачетной книжки не найден.",
        )

    except (IndexError, ValueError):
        await context.bot.send_message(
            chat_id=user_id,
            text="Неверный формат команды. Используйте: /zachotka 1234567",
        )


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("zachotka", get_attendance))

    application.run_polling()


if __name__ == "__main__":
    main()
