# EdvinBot - Discord helper bot

A Discord bot that fetches participants from [Raid-Helper](https://raid-helper.dev/) events and exports them as tab-separated text files for easy spreadsheet import.

## Prerequisites

- Python 3.8 or higher
- Discord bot token
- Raid-Helper event JSON URL

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Shiaulis/edvinBot.git
cd edvinBot
```

2. Create virtual environment (recommended):

```bash
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your Discord bot token:

```bash
echo "DISCORD_BOT_TOKEN=your_token_here" > .env
```

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Integrates with [Raid-Helper](https://raid-helper.dev/)
- Made with help of [Claude Code](https://claude.com/claude-code)
