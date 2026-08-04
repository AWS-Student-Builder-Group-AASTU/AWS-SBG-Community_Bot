import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot import (
    ADMIN_GROUP_ID,
    TELEGRAM_TOKEN,
    about_command,
    cancel_command,
    clear_proxy_environment,
    feedback_command,
    handle_admin_reply,
    handle_message,
    help_command,
    logger,
    start_command,
)


def main():
    """Creates the Telegram application and starts the polling loop."""
    clear_proxy_environment()

    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in environment variables.")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("cancel", cancel_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Chat(ADMIN_GROUP_ID) & (~filters.COMMAND),
            handle_admin_reply,
        )
    )

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("🤖 AWS Student Builder Feedback Bot is up and running...")
    app.run_polling()


if __name__ == "__main__":
    main()