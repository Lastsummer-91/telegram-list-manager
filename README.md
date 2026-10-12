# Telegram List Manager

Features: accepts text/TXT username lists up to 1,000 entries, removes duplicates, returns a cleaned TXT, creates an invite link for your configured group, and counts joins seen since the last restart.

Limitations: format checking does not confirm accounts exist. This bot does not scrape members or force-add people; members join voluntarily through an invite. The join count resets when the worker restarts. Keep BOT_TOKEN secret and never commit it to GitHub.

Environment variables:
- BOT_TOKEN: token from @BotFather
- ADMIN_ID: your numeric Telegram user ID
- GROUP_ID: target group's numeric chat ID (usually negative for supergroups)

Deploy as a Render Background Worker. Build command: `pip install -r requirements.txt`; start command: `python main.py`. Add the bot as group admin with invite permission.
