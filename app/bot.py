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
    for proxy_key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        os.environ.pop(proxy_key, None)

    os.environ.setdefault("NO_PROXY", "*")
    os.environ.setdefault("no_proxy", "*")


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
    "📘 **What we Can Do For You**\n\n"
    "• `/start` — Open the main welcome menu\n"
    "• `/feedback` — Drop a suggestion, idea, or issue for the core team\n"
    "• `/about` — Learn more about what we do\n"
    "• `/cancel` — Stop your current feedback draft\n\n"
    "💡 **Tip:** You can also tap the quick-action buttons at the bottom of your screen anytime!"
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
    if not update.message or not update.message.text:
        return

    text = update.message.text
    user = update.effective_user
    user_id = user.id

    # Handle button clicks text aliases
    if text == "📝 Submit Feedback":
        return await feedback_command(update, context)
    elif text == "ℹ️ About":
        return await about_command(update, context)
    elif text == "❓ Help":
        return await help_command(update, context)

    # Check if the user is currently in the feedback-writing state
    if user_states.get(user_id) == WAITING_FOR_FEEDBACK:
        # Reset state back to normal
        user_states[user_id] = None

        # Format feedback package for the admin core team
        username_str = f"@{user.username}" if user.username else "No username"
        admin_notification = (
            f"📥 **New AWS Community Feedback**\n\n"
            f"👤 **From:** {user.first_name} {user.last_name or ''} ({username_str})\n"
            f"🆔 **User ID:** `{user_id}`\n\n"
            f"💬 **Message:**\n{text}"
        )

        try:
            # Forward feedback to the student builder core team group
            if ADMIN_GROUP_ID != 0:
                sent_message = await context.bot.send_message(
                    chat_id=ADMIN_GROUP_ID,
                    text=admin_notification,
                )
                feedback_submissions[sent_message.message_id] = {
                    "sender_chat_id": user_id,
                    "sender_name": user.first_name,
                }

            # Restore the standard keyboard for the user
            reply_markup = get_main_menu_keyboard()

            # Confirm submission success to the member
            await update.message.reply_text(
                "✅ **Thank you!** Your feedback has been successfully delivered to the AWS Student Builder core team.",
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )

        except Exception as e:
            logger.error(f"Failed to forward feedback to admin group: {e}")
            await update.message.reply_text(
                "⚠️ Your feedback was received, but there was an error forwarding it to the team. Please try again later."
            )
    else:
        # Default response if they type random text outside of feedback flow
        await update.message.reply_text(
            "I didn't quite catch that. Use the button below or type `/feedback` to share your thoughts with us!",
            parse_mode="Markdown",
        )


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards an admin reply in the staff group back to the original member."""
    if not update.message or not update.message.reply_to_message:
        return

    replied_message_id = update.message.reply_to_message.message_id
    submission = feedback_submissions.get(replied_message_id)
    if not submission:
        return

    sender_chat_id = submission["sender_chat_id"]
    response_text = update.message.text or "(reply received)"
    await context.bot.send_message(
        chat_id=sender_chat_id,
        text=(
            f"💬 **Response from the AWS Student Builder core team**\n\n"
            f"{response_text}"
        ),
        parse_mode="Markdown",
    )

    # Clean up after delivering the reply.
    feedback_submissions.pop(replied_message_id, None)

