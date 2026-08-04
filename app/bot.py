import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_CHAT_ID", "0"))

# Enable logging to track activity and debug issues
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to track user conversation states (e.g., waiting for feedback text)
# In a larger version, this can be swapped out for a database like SQLite.
user_states = {}

# Maps a forwarded admin-group message id back to the original sender's chat id.
feedback_submissions = {}

# State constants
WAITING_FOR_FEEDBACK = "WAITING_FOR_FEEDBACK"


def get_main_menu_keyboard():
    """Returns the member-facing menu keyboard with command shortcuts."""
    return ReplyKeyboardMarkup(
        [["📝 Submit Feedback", "ℹ️ About"], ["❓ Help"], ["❌ Cancel"]],
        resize_keyboard=True,
    )


def clear_proxy_environment():
    """Disables inherited proxy environment variables that can block Telegram API access."""
    pass

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and a persistent keyboard option."""
    user = update.effective_user
    welcome_text = (
        f"👋 Hello **{user.first_name}**!\n\n"
        "Welcome to the **AWS Student Builder Group** Feedback Bot.\n"
        "We value your opinions, feature requests, and event suggestions.\n\n"
        "Use the menu below or type `/feedback` to share your thoughts."
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the available visible commands for members."""
    help_text = (
        "📘 **Member Commands**\n\n"
        "• `/start` — shows the welcome menu\n"
        "• `/help` — shows this help menu\n"
        "• `/feedback` — submit feedback to the core team\n"
        "• `/about` — learn more about the bot\n\n"
        "• `/cancel` — cancel the current feedback session\n\n"
        "You can also use the menu buttons below for quick access."
    )
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides details about the bot and community group."""
    about_text = (
        "ℹ️ **About This Bot**\n\n"
        "This is an official feedback channel for the AWS Student Builder community. "
        "Your submissions go directly to our core team to help us improve upcoming workshops, "
        "hackathons, and cloud training sessions."
    )
    await update.message.reply_text(
        about_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard(),
    )


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the feedback collection workflow."""
    user_id = update.effective_user.id
    user_states[user_id] = WAITING_FOR_FEEDBACK

    await update.message.reply_text(
        "✍️ Please type your feedback, suggestion, or issue below.\n\n"
        "*(Type /cancel if you change your mind)*",
        reply_markup=ReplyKeyboardRemove(),
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the current feedback session."""
    user_id = update.effective_user.id
    if user_states.get(user_id) == WAITING_FOR_FEEDBACK:
        user_states[user_id] = None
        
        keyboard = [["📝 Submit Feedback", "ℹ️ About"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text("❌ Feedback submission cancelled.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("No active action to cancel. Type /feedback to start.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes text messages based on the user's current state."""
    pass

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards an admin reply in the staff group back to the original member."""
    pass

def main():
    """Initializes and runs the Telegram bot."""
    clear_proxy_environment()

    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in environment variables.")
        return

    # Build application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("feedback", feedback_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("cancel", cancel_command))

    # Staff group replies should be routed back to the original member.
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Chat(ADMIN_GROUP_ID) & (~filters.COMMAND),
            handle_admin_reply,
        )
    )

    # Register general text message handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("🤖 AWS Student Builder Feedback Bot is up and running...")
    
    # Start polling for incoming messages
    app.run_polling()


if __name__ == "__main__":
    main()