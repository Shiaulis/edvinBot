# Discord Bot Setup Checklist

## Setup Steps

- [ ] Go to https://discord.com/developers/applications
- [ ] Create New Application (or select existing)
- [ ] Go to "Bot" tab
- [ ] Click "Reset Token" to get your bot token
- [ ] Enable these under "Privileged Gateway Intents":
  - Message Content Intent (optional, not needed for slash commands)
- [ ] Go to "OAuth2" > "URL Generator"
- [ ] Select scopes: `bot` and `applications.commands`
- [ ] Select bot permissions: `Send Messages`, `Use Slash Commands`
- [ ] Copy the generated URL and open in browser to invite bot to your server
- [ ] Copy `.env.example` to `.env` and add your bot token
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run the bot: `python raid_bot.py`

## Usage

Once the bot is running and invited to your server:

```
/raid-list url:https://raid-helper.dev/api/v2/events/YOUR_EVENT_ID
```

The bot will respond with a formatted list of participants in signup order.
