from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from app.api.cbr import CBRClient
from app.bot.keyboards import create_currencies_keyboard
from app.utils.text_utils import format_currency_message
from app.config import settings

cbr_client = CBRClient()

WAITING_FOR_CUSTOM_CODE = "waiting_for_custom_code"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    user = update.effective_user
    if not user:
        logger.error("Failed to retrieve user information")
        return

    user_id = user.id
    username = user.username or user.first_name

    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")

    keyboard = create_currencies_keyboard(settings.base_currencies)

    if not update.message:
        logger.error("Failed to retrieve message information from update")
        return

    await update.message.reply_text(
        f"Привет, {username}! Я помогу вам узнать курс ЦБ РФ на сегодня.\n\n"
        f"Выберите валюту из списка или нажмите 'Ввести свой код' "
        f"для проверки своей валюты (потребуется ввести трехбуквенный код, например, AED).",
        reply_markup=keyboard,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /help command."""

    if not update.message:
        logger.error("Failed to retrieve message information from update")
        return

    await update.message.reply_text(
        "🔹 Выберите валюту из кнопок для получения курса.\n"
        "🔹 Нажмите 'Ввести свой код' для проверки любой валюты по коду.\n"
        "🔹 Используйте команду /start для перезапуска бота.\n"
        "🔹 Данные предоставлены Центральным Банком России."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming messages from users."""
    user = update.effective_user
    if not user:
        logger.error("Failed to retrieve user information")
        return

    user_id = user.id
    if not update.message or not update.message.text:
        logger.error("Failed to retrieve message information from update or message text is empty")
        return

    message_text = update.message.text.strip()

    logger.debug(f"Получено сообщение от {user_id}: {message_text}")

    if not context.user_data:
        context.user_data.clear()

    if context.user_data.get(WAITING_FOR_CUSTOM_CODE):
        await handle_custom_currency(update, context, message_text)
        return

    if message_text.upper() == "ВВЕСТИ СВОЙ КОД":
        context.user_data[WAITING_FOR_CUSTOM_CODE] = True
        logger.info(f"User {user_id} requested currency code input")

        await update.message.reply_text("Введите международный код валюты (например, USD, EUR, GBP):")
        return

    currency_code = message_text.upper()
    if currency_code in settings.base_currencies:
        await get_currency_rate(update, context, currency_code)
    else:
        await update.message.reply_text("Пожалуйста, выберите валюту из кнопок или нажмите 'Ввести свой код'.")


async def handle_custom_currency(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> None:
    """Handles the custom currency code input by the user."""
    if not update.effective_message:
        logger.error("Failed to retrieve message information from update")
        return

    user_id = update.effective_user.id
    currency_code = message_text.strip().upper()

    # Сбрасываем состояние ожидания
    context.user_data[WAITING_FOR_CUSTOM_CODE] = False

    # Проверяем формат кода валюты
    if not (len(currency_code) == 3 and currency_code.isalpha()):
        logger.warning(f"Пользователь {user_id} ввел некорректный код валюты: {currency_code}")

        if not update.message:
            logger.error("Failed to retrieve message information from update")
            return

        await update.message.reply_text(
            "❌ Некорректный формат кода валюты. Пожалуйста, введите трехбуквенный код (например, USD)."
        )
        return

    # Запрашиваем курс валюты
    await get_currency_rate(update, context, currency_code)


async def get_currency_rate(update: Update, context: ContextTypes.DEFAULT_TYPE, currency_code: str) -> None:
    """Gets the currency rate from the CBR API and sends it to the user."""
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} запросил курс валюты: {currency_code}")

    if not update.message:
        logger.error("Failed to retrieve message information from update")
        return

    await update.message.reply_text("⏳ Получаю данные...")

    # Получаем данные о курсе валюты
    currency_data = await cbr_client.get_currency_rate(currency_code)

    if currency_data:
        # Форматируем и отправляем сообщение с курсом
        message = format_currency_message(currency_data)
        logger.info(f"Successfully sent the amount in {currency_code} to the user {user_id}")

        await update.message.reply_text(message)
    else:
        logger.warning(f"Failed to find the exchange rate {currency_code} for user {user_id}")

        await update.message.reply_text(
            f"❌ Не удалось получить курс валюты {currency_code}.\n"
            f"Проверьте правильность кода валюты или попробуйте позже."
        )
