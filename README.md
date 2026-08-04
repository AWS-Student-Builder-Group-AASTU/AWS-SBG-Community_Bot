# AWS SBG Community Bot

A Telegram bot for the AWS Student Builder Group community that lets members submit feedback, suggestions, and issues directly to the admin/core team.

## What the bot does

The bot gives community members a fast and friendly way to:

- open the bot and see a visible menu
- view help and command shortcuts
- submit feedback through `/feedback`
- learn more about the community channel through `/about`

Once a member sends feedback, the bot forwards the message to the configured admin group. If an admin replies to that forwarded message, the bot sends the reply back to the original member.

## Member experience

Members can use either Telegram commands or the visible reply keyboard buttons.

### Commands

- `/start` — opens the welcome screen and menu
- `/help` — displays the visible command list
- `/feedback` — starts the feedback submission flow
- `/about` — explains the purpose of the bot
- `/cancel` — stops the current feedback draft

### Visible keyboard options

The main menu presents these quick actions:

- `📝 Submit Feedback`
- `ℹ️ About`
- `❓ Help`
- `❌ Cancel`

## Feedback response workflow

1. A member opens the bot and starts a feedback flow.
2. The bot asks the member to send their feedback text.
3. The bot forwards the message to the configured admin group.
4. An admin replies to that forwarded message in the admin group.
5. The bot looks up the original recipient and sends the admin reply back to the member.

## Project structure

- `main.py` — repository-level startup entrypoint that builds the Telegram application and begins polling
- `app/bot.py` — bot logic, command handlers, keyboard setup, feedback forwarding, and admin reply routing
- `.env` — environment values, including the Telegram token and admin group chat ID
- `requirements.txt` — Python dependency list for the project

## Setup

1. Create and activate a Python virtual environment.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following values:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_GROUP_CHAT_ID=your_admin_group_chat_id
```

4. Start the bot from the repository root launcher:

```bash
python main.py
```

> The runtime is intentionally separated: `main.py` handles startup, while `app/bot.py` contains the bot behavior and message flow.

## Contributor workflow

Collaborators can improve the bot by following the same setup process and expanding the member/admin experience.

### Contributor setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the project dependencies.
4. Copy your token and admin group ID into a local `.env` file.
5. Run the bot locally using `python main.py`.

### Good collaboration areas

Contributors can help with:

- improving the welcome/help UX
- refining the forwarding format shown to the admin group
- adding more graceful handling for cancel and retry flows
- moving the feedback tracking state from memory to a persistent database
- adding logging, moderation, or analytics support
- improving project documentation and contributor guidance

### Recommended contribution flow

1. Create a feature branch.
2. Make small, focused changes.
3. Verify the bot still compiles in the project environment.
4. Test the command and feedback flow manually in Telegram.
5. Open a pull request with a short summary of the behavior change.

## Notes

- The bot currently uses an in-memory mapping to connect a forwarded admin-group message back to the original sender.
- Proxy environment variables are cleared during startup so Telegram API requests can succeed in environments where a proxy would otherwise block them.
- The current implementation is intentionally lightweight and is a strong base for future persistence, moderation, analytics, and admin tooling.
- Only one bot instance should be polling Telegram for the same bot token at a time. Running multiple instances of the same bot can cause Telegram `getUpdates` conflicts.
