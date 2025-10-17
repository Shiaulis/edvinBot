#!/usr/bin/env python3
"""
main.py

Discord bot that fetches Raid-Helper participants and posts them in signup order.
"""

import os
import io
import logging
import discord
from discord import app_commands
import aiohttp
from typing import Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Bot setup - minimal intents for slash commands only
intents = discord.Intents.none()
intents.guilds = True  # Required for slash commands in guilds
intents.dm_messages = True  # Required for DM interactions

class RaidBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.session = None

    async def setup_hook(self):
        # Create persistent HTTP session with connection pooling
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=10)
        )
        await self.tree.sync()

    async def close(self):
        # Clean up session on shutdown
        if self.session:
            await self.session.close()
        await super().close()

bot = RaidBot()

# Constants
JSON_KEY = "signUps"
MAX_POSITION_FALLBACK = 10**9  # Fallback for missing position values
RAID_HELPER_DOMAIN = "raid-helper.dev"


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
    """Fetch JSON data from Raid-Helper URL asynchronously."""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


def format_participants(signups: list[dict[str, Any]]) -> str:
    """Format participants list in signup order with name and status."""
    # Sort by position (ascending), fall back to entryTime if position missing
    signups = sorted(signups, key=lambda e: (e.get("position", MAX_POSITION_FALLBACK), e.get("entryTime", 0)))

    return "\n".join(
        f"{entry.get('name', 'Unknown')}\t{entry.get('className', 'unknown')}"
        for entry in signups
    )


@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f"Logged in as {bot.user}")
    logger.info(f"Synced {len(bot.tree.get_commands())} command(s)")


@bot.tree.command(name="raid-list", description="Fetch and display Raid-Helper participants")
@app_commands.describe(url="Raid-Helper JSON URL")
async def raid_list(interaction: discord.Interaction, url: str):
    """Slash command to fetch raid participants."""
    # Log the request
    location = f"Guild: {interaction.guild.name}" if interaction.guild else "DM"
    logger.info(f"[RAID-LIST] Request from {interaction.user.name} in {location} | URL: {url}")

    await interaction.response.defer()

    try:
        # Validate URL is from raid-helper.dev
        if RAID_HELPER_DOMAIN not in url.lower():
            await interaction.followup.send(f"Invalid URL. Please provide a {RAID_HELPER_DOMAIN} URL.")
            logger.warning(f"Invalid URL rejected from {interaction.user.name}: {url}")
            return

        # Fetch data using persistent session
        data = await fetch_json(bot.session, url)
        signups: list[dict[str, Any]] = data.get(JSON_KEY, [])

        if not signups:
            logger.info(f"No participants found for URL: {url}")
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
        logger.info(f"Successfully sent {len(signups)} participants to {interaction.user.name}")

    except aiohttp.ClientError as e:
        error_msg = f"Failed to fetch data: {str(e)}"
        logger.error(f"HTTP error for {interaction.user.name}: {error_msg}")
        await interaction.followup.send(error_msg)
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logger.error(f"Unexpected error for {interaction.user.name}: {error_msg}", exc_info=True)
        await interaction.followup.send(error_msg)


def main():
    """Run the bot."""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables")
        return

    logger.info("Starting bot...")

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token. Please check your DISCORD_BOT_TOKEN in Railway variables.")
    except Exception as e:
        logger.error(f"Error starting bot: {type(e).__name__}: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
