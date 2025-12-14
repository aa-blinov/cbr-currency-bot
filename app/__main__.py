import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from loguru import logger
from telegram import Update

from app.config import settings
from app.bot.handlers import start_command, help_command, handle_message, stats_command
from app.stats.service import StatsService


async def post_init(application: Application) -> None:
    """Initialize services after application creation."""
    stats_service = StatsService()
    await stats_service.initialize()
    logger.info("Statistics service initialized")


def main() -> None:
    """Main function to run the Telegram bot."""
    logger.info("Launching a Telegram bot for exchange rates")

    try:
        application = Application.builder().token(settings.telegram_token).post_init(post_init).build()

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", stats_command))

        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        logger.info("The bot has been successfully launched and is ready to work")

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as exc:
        logger.exception(f"Critical error while starting the bot: {exc}")
        raise


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot was stopped")
    except Exception as exc:
        logger.critical(f"Unexpected error: {exc}")
        sys.exit(1)
