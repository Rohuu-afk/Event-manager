import os
import discord
from discord.ext import commands
import json
import logging
import asyncio
import signal
from datetime import datetime

# Setup logging with more detailed DEBUG level
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResilientBot(commands.Bot):
    def __init__(self):
        # Setup proper intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required for commands to work
        intents.members = True          # Required for member-related features
        intents.guilds = True           # Required for guild-related features
        super().__init__(command_prefix="!", intents=intents)

        # Load points data
        self.points = self.load_points()
        self.last_save = datetime.now()

        # Track reconnection attempts
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds

        # Register signal handlers for clean shutdown
        signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.close()))
        signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.close()))

    def load_points(self):
        try:
            with open("points.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.info("No points file found, starting fresh")
            return {}
        except Exception as e:
            logger.error(f"Error loading points: {e}")
            return {}

    async def save_points(self):
        try:
            with open("points.json", "w") as f:
                json.dump(self.points, f)
            self.last_save = datetime.now()
            logger.debug("Points data saved successfully")
        except Exception as e:
            logger.error(f"Error saving points data: {e}")

    async def setup_hook(self):
        """Setup hook to initialize bot components"""
        try:
            # Load cogs
            for cog in ['basic_commands', 'error_handler', 'points_commands']:
                try:
                    await self.load_extension(f'cogs.{cog}')
                    logger.info(f"Successfully loaded cog: {cog}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog}: {e}")
                    raise

            logger.info("All cogs loaded successfully")

            # Start periodic save task
            self.loop.create_task(self.periodic_save())
        except Exception as e:
            logger.error(f"Error in setup: {e}")
            raise

    async def periodic_save(self):
        while not self.is_closed():
            await asyncio.sleep(300)  # Save every 5 minutes
            await self.save_points()

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Command prefix: {self.command_prefix}')
        logger.info(f'Loaded cogs: {", ".join([cog for cog in self.cogs])}')
        logger.info(f'Available commands: {", ".join([cmd.name for cmd in self.commands])}')
        self.reconnect_attempts = 0  # Reset reconnect attempts on successful connection

    async def on_message(self, message):
        """Handle message events and process commands"""
        if message.author.bot:
            return

        logger.debug(f"Received message: {message.content} from {message.author}")

        # Process commands
        try:
            await self.process_commands(message)
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            logger.error(f"Full traceback: {e.__traceback__}")

    async def on_command(self, ctx):
        """Log when commands are invoked"""
        logger.info(f"Command '{ctx.command.name}' invoked by {ctx.author}")

    async def on_command_error(self, ctx, error):
        """Log command errors"""
        logger.error(f"Error in command '{ctx.command}' invoked by {ctx.author}: {error}")

    async def on_disconnect(self):
        logger.warning("Bot disconnected from Discord")
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect... (Attempt {self.reconnect_attempts})")
            await asyncio.sleep(self.reconnect_delay)
        else:
            logger.error("Maximum reconnection attempts reached. Please check your connection.")

    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down bot...")
        await self.save_points()  # Save points before closing
        await super().close()

async def main():
    """Main function to run the bot"""
    bot = ResilientBot()

    try:
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("No Discord token found in environment variables")

        async with bot:
            await bot.start(token)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())