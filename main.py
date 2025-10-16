#!/usr/bin/env python3
"""
raid_bot.py

Discord bot that fetches Raid-Helper participants and posts them in signup order.
"""

import os
import io
import discord
from discord import app_commands
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot setup - minimal intents for slash commands only
intents = discord.Intents.none()
intents.guilds = True  # Required for slash commands in guilds
intents.dm_messages = True  # Required for DM interactions

class RaidBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = RaidBot()

JSON_KEY = "signUps"


def fetch_json(url: str) -> Dict:
    """Fetch JSON data from Raid-Helper URL."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def format_participants(signups: List[Dict]) -> str:
    """Format participants list in signup order with name and status."""
    # Sort by position (ascending), fall back to entryTime if position missing
    signups = sorted(signups, key=lambda e: (e.get("position", 10**9), e.get("entryTime", 0)))

    lines = []
    for entry in signups:
        name = entry.get("name", "Unknown")
        status = entry.get("className", "unknown")
        lines.append(f"{name}\t{status}")

    return "\n".join(lines)


@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f"Logged in as {bot.user}")
    print(f"Synced {len(bot.tree.get_commands())} command(s)")


@bot.tree.command(name="raid-list", description="Fetch and display Raid-Helper participants")
@app_commands.describe(url="Raid-Helper JSON URL")
async def raid_list(interaction: discord.Interaction, url: str):
    """Slash command to fetch raid participants."""
    await interaction.response.defer()

    try:
        # Fetch data
        data = fetch_json(url)
        signups: List[Dict] = data.get(JSON_KEY, [])

        if not signups:
            await interaction.followup.send("No participants found in this raid.")
            return

        # Format output
        formatted = format_participants(signups)

        # Create file attachment with tab-separated values
        file_buffer = io.BytesIO(formatted.encode('utf-8'))
        file = discord.File(file_buffer, filename="raid_participants.txt")

        await interaction.followup.send(
            f"Found {len(signups)} participants:",
            file=file
        )

    except requests.RequestException as e:
        await interaction.followup.send(f"Failed to fetch data: {str(e)}")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")


def main():
    """Run the bot."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        print("Create a .env file with: DISCORD_BOT_TOKEN=your_token_here")
        return

    bot.run(token)


if __name__ == "__main__":
    main()
