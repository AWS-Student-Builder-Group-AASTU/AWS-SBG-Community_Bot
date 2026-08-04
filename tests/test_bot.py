import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.bot as bot


class FakeUser:
    def __init__(self, user_id=42, first_name="Test", last_name=None, username="tester"):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username


class FakeMessage:
    def __init__(self, text="", chat_id=1):
        self.text = text
        self.chat_id = chat_id
        self.reply_text_calls = []
        self.reply_to_message = None

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.reply_text_calls.append(
            {
                "text": text,
                "parse_mode": parse_mode,
                "reply_markup": reply_markup,
            }
        )


class FakeUpdate:
    def __init__(self, user_id=42, text="", chat_id=1, reply_to_message_id=None):
        self.effective_user = FakeUser(user_id=user_id)
        self.message = FakeMessage(text=text, chat_id=chat_id)
        if reply_to_message_id is not None:
            self.message.reply_to_message = type(
                "ReplyToMessage", (), {"message_id": reply_to_message_id}
            )()


class FakeBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, chat_id, text, parse_mode=None):
        message_id = len(self.sent_messages) + 1
        self.sent_messages.append((chat_id, text, message_id, parse_mode))
        return type("SentMessage", (), {"message_id": message_id})()


class FakeContext:
    def __init__(self):
        self.bot = FakeBot()


def test_get_main_menu_keyboard_contains_expected_actions():
    keyboard = bot.get_main_menu_keyboard()

    labels = [
        [button.text for button in row]
        for row in keyboard.keyboard
    ]

    assert labels == [
        ["📝 Submit Feedback", "ℹ️ About"],
        ["❓ Help"],
        ["❌ Cancel"],
    ]


def test_clear_proxy_environment_removes_proxy_variables_and_sets_no_proxy():
    os.environ["HTTP_PROXY"] = "http://example.com"
    os.environ["HTTPS_PROXY"] = "http://example.com"
    os.environ["ALL_PROXY"] = "http://example.com"
    os.environ["no_proxy"] = "localhost"

    bot.clear_proxy_environment()

    assert "HTTP_PROXY" not in os.environ
    assert "HTTPS_PROXY" not in os.environ
    assert "ALL_PROXY" not in os.environ
    assert os.environ["NO_PROXY"] == "*"
    assert os.environ["no_proxy"] == "*"


def test_help_command_returns_expected_shortcuts():
    update = FakeUpdate(user_id=555)
    context = FakeContext()

    asyncio.run(bot.help_command(update, context))

    assert update.message.reply_text_calls[0]["text"].startswith("📘")
    assert "`/start`" in update.message.reply_text_calls[0]["text"]


def test_feedback_command_sets_waiting_state_and_removes_keyboard():
    update = FakeUpdate(user_id=111)
    context = FakeContext()

    asyncio.run(bot.feedback_command(update, context))

    assert bot.user_states[111] == bot.WAITING_FOR_FEEDBACK
    assert update.message.reply_text_calls[0]["reply_markup"] is not None


def test_cancel_command_clears_feedback_state_and_restores_keyboard():
    update = FakeUpdate(user_id=222)
    context = FakeContext()
    bot.user_states[222] = bot.WAITING_FOR_FEEDBACK

    asyncio.run(bot.cancel_command(update, context))

    assert bot.user_states[222] is None
    assert update.message.reply_text_calls[0]["text"] == "❌ Feedback submission cancelled."

    labels = [
        [button.text for button in row]
        for row in update.message.reply_text_calls[0]["reply_markup"].keyboard
    ]
    assert labels == [["📝 Submit Feedback", "ℹ️ About"]]


def test_handle_message_forwards_feedback_to_admin_group_and_returns_success():
    original_admin_group_id = bot.ADMIN_GROUP_ID
    bot.ADMIN_GROUP_ID = 999
    bot.user_states.clear()
    bot.feedback_submissions.clear()

    update = FakeUpdate(user_id=333, text="This is a test feedback message")
    context = FakeContext()
    bot.user_states[333] = bot.WAITING_FOR_FEEDBACK

    asyncio.run(bot.handle_message(update, context))

    assert len(context.bot.sent_messages) == 1
    chat_id, text, message_id, parse_mode = context.bot.sent_messages[0]
    assert chat_id == 999
    assert parse_mode is None
    assert "📥 **New AWS Community Feedback**" in text
    assert "This is a test feedback message" in text
    assert bot.feedback_submissions[message_id]["sender_chat_id"] == 333
    assert update.message.reply_text_calls[-1]["text"].startswith("✅ **Thank you!")
    assert bot.user_states[333] is None

    bot.ADMIN_GROUP_ID = original_admin_group_id


def test_handle_admin_reply_routes_staff_reply_back_to_original_member():
    bot.feedback_submissions.clear()
    context = FakeContext()
    update = FakeUpdate(user_id=444, text="Thanks for sharing this.")
    update.message.reply_to_message = type(
        "ReplyToMessage", (), {"message_id": 7}
    )()
    bot.feedback_submissions[7] = {
        "sender_chat_id": 444,
        "sender_name": "Original User",
    }

    asyncio.run(bot.handle_admin_reply(update, context))

    assert len(context.bot.sent_messages) == 1
    chat_id, text, _, parse_mode = context.bot.sent_messages[0]
    assert chat_id == 444
    assert parse_mode == "Markdown"
    assert "💬 **Response from the AWS Student Builder core team**" in text
    assert "Thanks for sharing this." in text
    assert 7 not in bot.feedback_submissions
