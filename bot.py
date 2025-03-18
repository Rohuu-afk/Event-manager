import os
import discord
from discord.ext import commands
import json
import logging
import asyncio
import signal
from datetime import datetime

# Setup logging with detailed DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EventAvengerBot(commands.Bot):
    def __init__(self):
        # Setup proper intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required for commands to work
        intents.members = True          # Required for member-related features
        intents.guilds = True           # Required for guild-related features

        super().__init__(command_prefix="!", intents=intents)

        # Points system
        self.points = {}
        self.load_points()

        # Register signal handlers
        signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.close()))
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.close()))

    def load_points(self):
        """Load points from JSON file"""
        try:
            with open("points.json", "r") as f:
                self.points = json.load(f)
                logger.info("Points loaded successfully")
        except FileNotFoundError:
            logger.info("No points file found, starting fresh")
            self.points = {}
        except Exception as e:
            logger.error(f"Error loading points: {e}")
            self.points = {}

    async def save_points(self):
        """Save points to JSON file"""
        try:
            with open("points.json", "w") as f:
                json.dump(self.points, f)
            logger.info("Points saved successfully")
        except Exception as e:
            logger.error(f"Error saving points: {e}")

    async def setup_hook(self):
        """Setup hook to load cogs and start tasks"""
        try:
            # Load cogs
            for cog in ['basic_commands', 'error_handler', 'points_commands']:
                try:
                    await self.load_extension(f'cogs.{cog}')
                    logger.info(f"Successfully loaded cog: {cog}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog}: {e}")
                    raise

            # Start periodic save task
            self.loop.create_task(self.periodic_save())
            logger.info("All setup tasks completed")
        except Exception as e:
            logger.error(f"Error in setup: {e}")
            raise

    async def periodic_save(self):
        """Periodically save points data"""
        while not self.is_closed():
            await asyncio.sleep(300)  # Save every 5 minutes
            await self.save_points()

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Command prefix: {self.command_prefix}')
        logger.info(f'Loaded cogs: {", ".join([cog for cog in self.cogs])}')
        logger.info(f'Available commands: {", ".join([cmd.name for cmd in self.commands])}')

    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down bot...")
        await self.save_points()
        await super().close()

async def main():
    """Main function to run the bot"""
    bot = EventAvengerBot()

    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("No Discord token found in environment variables")

        async with bot:
            await bot.start(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())