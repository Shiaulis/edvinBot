#!/usr/bin/env python3
"""
main.py

Discord bot that fetches Raid-Helper participants and posts them in signup order.
"""

import os
import io
import logging
import time
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
        self.last_request_time: dict[int, float] = {}  # Track last request time per user ID

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
RATE_LIMIT_SECONDS = 10  # Minimum seconds between requests per user


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
    """Fetch JSON data from Raid-Helper URL asynchronously."""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


def format_participants(signups: list[dict[str, Any]]) -> str:
    """Format participants list in signup order with name and class (tab-separated)."""
    # Sort by position (ascending), fall back to entryTime if position missing
    signups = sorted(signups, key=lambda e: (e.get("position", MAX_POSITION_FALLBACK), e.get("entryTime", 0)))

    return "\n".join(
        f"{entry.get('name', 'Unknown')}\t{entry.get('className', 'unknown')}"
        for entry in signups
    )


def sanitize_filename(title: str, date: str) -> str:
    """Create a safe filename from event title and date."""
    # Remove or replace unsafe characters
    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)
    safe_title = safe_title.strip().replace(' ', '_')
    # Limit length
    if len(safe_title) > 50:
        safe_title = safe_title[:50]
    return f"{safe_title}_{date}.txt" if safe_title else f"raid_{date}.txt"


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
        # Check rate limiting
        user_id = interaction.user.id
        current_time = time.time()
        last_request = bot.last_request_time.get(user_id, 0)
        time_since_last = current_time - last_request

        if time_since_last < RATE_LIMIT_SECONDS:
            wait_time = int(RATE_LIMIT_SECONDS - time_since_last)
            await interaction.followup.send(f"Please wait {wait_time} seconds before requesting again.")
            logger.info(f"Rate limit hit for {interaction.user.name}")
            return

        # Validate URL is from raid-helper.dev
        if RAID_HELPER_DOMAIN not in url.lower():
            await interaction.followup.send(f"Invalid URL. Please provide a {RAID_HELPER_DOMAIN} URL.")
            logger.warning(f"Invalid URL rejected from {interaction.user.name}: {url}")
            return

        # Update last request time
        bot.last_request_time[user_id] = current_time

        # Fetch data using persistent session
        data = await fetch_json(bot.session, url)

        # Validate JSON structure
        if not isinstance(data, dict):
            logger.error(f"Invalid JSON structure: expected dict, got {type(data)}")
            await interaction.followup.send("Invalid data format received from raid-helper.")
            return

        signups: list[dict[str, Any]] = data.get(JSON_KEY, [])

        if not signups:
            logger.info(f"No participants found for URL: {url}")
            await interaction.followup.send("No participants found in this raid.")
            return

        # Get event metadata for filename
        event_title = data.get("title", "raid")
        event_date = data.get("date", "unknown")
        filename = sanitize_filename(event_title, event_date)

        # Format output
        formatted = format_participants(signups)

        # Create file attachment with tab-separated values
        file_buffer = io.BytesIO(formatted.encode('utf-8'))
        file = discord.File(file_buffer, filename=filename)

        await interaction.followup.send(
            f"Found {len(signups)} participants:",
            file=file
        )
        logger.info(f"Successfully sent {len(signups)} participants to {interaction.user.name}")

    except aiohttp.ClientResponseError as e:
        # Handle specific HTTP error codes
        if e.status == 404:
            error_msg = "Event not found. Please check the URL and try again."
        elif e.status == 403:
            error_msg = "Access denied. The event may be private."
        elif e.status == 429:
            error_msg = "Rate limited by raid-helper. Please try again later."
        elif e.status >= 500:
            error_msg = "Raid-helper server error. Please try again later."
        else:
            error_msg = f"Failed to fetch data (HTTP {e.status})"

        logger.error(f"HTTP {e.status} error for {interaction.user.name}: {url}")
        await interaction.followup.send(error_msg)
    except aiohttp.ClientError as e:
        error_msg = f"Network error: {str(e)}"
        logger.error(f"Network error for {interaction.user.name}: {error_msg}")
        await interaction.followup.send("Network error. Please check the URL and try again.")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        logger.error(f"Unexpected error for {interaction.user.name}: {error_msg}", exc_info=True)
        await interaction.followup.send("An unexpected error occurred. Please try again later.")


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
