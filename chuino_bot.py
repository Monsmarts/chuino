"""
Чуйно — Telegram бот
Анонімно пересилає повідомлення від користувачів власнику каналу.

Встановлення:
    pip uninstall python-telegram-bot -y
    pip install "python-telegram-bot==21.9"

Налаштування:
    1. Створи бота через @BotFather — отримаєш BOT_TOKEN
    2. Дізнайся свій OWNER_CHAT_ID через @userinfobot
    3. Встав обидва значення нижче
    4. Запусти: python chuino_bot.py
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ──────────────────────────────────────────────
#  НАЛАШТУВАННЯ — змінити перед запуском
# ──────────────────────────────────────────────
BOT_TOKEN = "8524048311:AAFE6SZsAkSCxVj3TRppu6ILBXV2-iwypPc"
OWNER_CHAT_ID = 424389039

# ──────────────────────────────────────────────
#  Тексти
# ──────────────────────────────────────────────
WELCOME = (
    "Привіт 🌿\n\n"
    "Всім нам час від часу потрібно виговоритись. Але часто навіть найближчі люди втомлюються слухати.\n\n"
    "Розмови з ШІ навіюють відчуття синтетичності і не дають того полегшення. Тут слухає і відповідає жива людина. Напиши все, що лежить на душі. Я прочитаю і відповім по-людськи.\n"
    "Твоє ім'я залишиться анонімним, я не знаю, хто ти.\n\n"
    "Коли бот надішле мені анонімне повідомлення, я відповім на нього. Так ти отримаєш відповідь. Все безкоштовно 🤍"
)

RECEIVED = (
    "Отримала 🤍\n\n"
    "Я прочитаю і одразу відпишу.\n"
    "Поки що можна переглянути цікаві пости у нашому каналі t.me/chuino"
)

OWNER_PREFIX = "💬 Нове анонімне повідомлення:\n\n"
REPLY_SENT = "Відповідь надіслано 🤍"
REPLY_ERROR = "Не вдалось надіслати — можливо, людина заблокувала бота."
HELP_TEXT = (
    "Просто напиши що думаєш — я отримаю і відповім.\n"
    "Все анонімно через бота, я не бачу імен 🌿"
)

# ──────────────────────────────────────────────
#  Логування
# ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
#  Хендлери
# ──────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id == OWNER_CHAT_ID:
        return

    text = update.message.text or "[не текст]"
    forwarded = (
        f"{OWNER_PREFIX}{text}\n\n"
        f"↩️ Відповісти: /reply_{user_id}"
    )

    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=forwarded)
        await update.message.reply_text(RECEIVED)
    except Exception as e:
        logger.error(f"Помилка пересилання: {e}")


async def handle_owner_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_CHAT_ID:
        return

    msg = update.message.text or ""
    parts = msg.split(" ", 1)

    if len(parts) < 2:
        await update.message.reply_text(
            "Формат: /reply_<chat_id> <текст>\n"
            "Приклад: /reply_123456789 Я тебе чую 🤍"
        )
        return

    try:
        target_id = int(parts[0].replace("/reply_", ""))
    except ValueError:
        await update.message.reply_text("Не вдалось розпізнати chat_id.")
        return

    try:
        await context.bot.send_message(chat_id=target_id, text=f"🤍\n\n{parts[1].strip()}")
        await update.message.reply_text(REPLY_SENT)
    except Exception as e:
        logger.error(f"Помилка відповіді: {e}")
        await update.message.reply_text(REPLY_ERROR)


# ──────────────────────────────────────────────
#  Запуск — сумісний з Python 3.14
# ──────────────────────────────────────────────
async def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"^/reply_\d+") & filters.Chat(OWNER_CHAT_ID),
            handle_owner_reply,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_user_message,
        )
    )

    logger.info("Бот запущено 🌿")
    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        await asyncio.Event().wait()  # тримаємо бота живим


if __name__ == "__main__":
    asyncio.run(main())
