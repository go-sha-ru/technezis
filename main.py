import os
import logging
import pandas as pd

from tabulate import tabulate
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from data import init_db, save_data

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WITH_PRICE = os.getenv("WITH_PRICE")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

FILE, PROCESS = 1, 2

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        f"Здравствуйте {user.first_name}, прикрепите файл Excel",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FILE


async def get_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    excel_file = await update.message.effective_attachment.get_file()
    f_name = f'{excel_file.file_id}.xlsx'
    await excel_file.download_to_drive(f_name)
    logger.info(f"Файл {user.first_name}: {f_name}")
    data = pd.read_excel(f_name)    
    init_db()
    save_data(data=data, with_price=True)
    avg = ""
    maxcolwidths = [30, 30, None]
    if WITH_PRICE:
        maxcolwidths = [30, 30, 30, 30]
        avg = f'\nСредняя цена: {data.loc[:, 'price'].mean()}'
    output = tabulate(data, headers='keys', showindex=False, maxcolwidths=maxcolwidths, tablefmt='grid')    
    await update.message.reply_text(f"<pre>{output}{avg}</pre>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"Пользователь {user.first_name} отменил.")
    await update.message.reply_text(
        "Спасибо", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FILE: [MessageHandler(filters.ATTACHMENT, get_file)],            
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
