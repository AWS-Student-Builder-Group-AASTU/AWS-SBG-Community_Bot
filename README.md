# AWS SBG Community Bot

A Telegram bot for the AWS Student Builder Group community that lets members submit feedback, suggestions, and issues directly to the admin/core team.

## What the bot does

The bot provides a simple and friendly interface for community members to:

- start a conversation with the bot
- view the available help and command shortcuts
- submit feedback through `/feedback`
- read the bot’s about information through `/about`

Once a member sends feedback, the bot forwards that message to the configured admin group. If an admin replies to the forwarded message in the admin group, the bot routes the response back to the original member.

## Available commands

Members can use either the Telegram command interface or the visible reply keyboard buttons.

- `/start` — shows the welcome screen and main menu
- `/help` — shows the visible command list
- `/feedback` — starts the feedback submission flow
- `/about` — explains the purpose of the bot

The keyboard menu includes these visible options:

- `📝 Submit Feedback`
- `ℹ️ About`
- `❓ Help`

## Workflow

1. A member opens the bot and chooses `/feedback` or the feedback button.
2. The bot asks the member to type their feedback.
3. The member’s message is sent to the configured admin group.
4. A core team/admin member replies to that forwarded message in the admin group.
5. The bot sends the admin reply back to the original member.

## Project structure

- `app/bot.py` — main Telegram bot implementation
- `.env` — environment variables such as the Telegram bot token and admin group chat ID

## Setup

1. Create and activate a Python virtual environment.
2. Install the required dependencies:

```bash
pip install python-telegram-bot python-dotenv
```

3. Create a `.env` file with the following values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_GROUP_CHAT_ID=your_admin_group_chat_id
```

4. Run the bot:

```bash
python app/bot.py
```

## Contributing / Collaborator workflow

Collaborators can help improve the bot by following the same local setup steps and then extending the command and feedback experience.

### Contributor setup

1. Clone the repository.
2. Create a virtual environment.
3. Install the dependencies.
4. Copy the environment settings into a local `.env` file.
5. Run the bot locally for testing.

### Good collaboration areas

Contributors can help with:

- improving the welcome and help menu UX
- refining the admin feedback message format
- adding better handling for `/cancel` and other command flows
- moving the submission mapping from memory to a database
- adding logging, analytics, or moderation workflows
- improving the README and developer documentation

### Recommended contribution workflow

1. Create a feature branch.
2. Make small, focused changes.
3. Verify the bot still compiles with the project environment.
4. Test the command flow manually in Telegram.
5. Open a pull request with a short summary of the behavior change.

## Notes

- The bot uses a local in-memory mapping to connect a forwarded admin-group message back to the original sender.
- Proxy environment variables are cleared at startup so Telegram API calls can connect directly in environments where a proxy would otherwise block requests.
- The current bot flow is intentionally simple and is a good base for future enhancements such as persistence, better moderation, or admin analytics.
