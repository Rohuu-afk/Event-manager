import os
import discord
from discord.ext import commands
import json
import matplotlib.pyplot as plt
import io
import numpy as np
from PIL import Image
import logging
import asyncio
import signal
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResilientBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
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
        self.loop.create_task(self.periodic_save())

    async def periodic_save(self):
        while not self.is_closed():
            await asyncio.sleep(300)  # Save every 5 minutes
            await self.save_points()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        self.reconnect_attempts = 0  # Reset reconnect attempts on successful connection

    async def on_disconnect(self):
        logger.warning("Bot disconnected from Discord")
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect... (Attempt {self.reconnect_attempts})")
            await asyncio.sleep(self.reconnect_delay)
        else:
            logger.error("Maximum reconnection attempts reached. Please check your connection.")

    @commands.command()
    async def addpoints(self, ctx, user: discord.Member, amount: int):
        """Add points to a user"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command.")
            return

        user_id = str(user.id)
        self.points[user_id] = self.points.get(user_id, 0) + amount
        await self.save_points()
        await ctx.send(f"Added {amount} points to {user.display_name}. Total points: {self.points[user_id]}")

    @commands.command()
    async def removepoints(self, ctx, user: discord.Member, amount: int):
        """Remove points from a user"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You don't have permission to use this command.")
            return

        user_id = str(user.id)
        self.points[user_id] = max(0, self.points.get(user_id, 0) - amount)
        await self.save_points()
        await ctx.send(f"Removed {amount} points from {user.display_name}. Total points: {self.points[user_id]}")

    @commands.command()
    async def leaderboard(self, ctx):
        """Display the points leaderboard"""
        try:
            sorted_points = sorted(self.points.items(), key=lambda x: x[1], reverse=True)[:10]
            users = [ctx.guild.get_member(int(user_id)) for user_id, _ in sorted_points]
            scores = [score for _, score in sorted_points]

            # Create leaderboard visualization
            plt.style.use('dark_background')
            fig = plt.figure(figsize=(10, len(users) * 0.8))
            ax = plt.gca()
            fig.patch.set_facecolor('#2C2F33')
            ax.set_facecolor('#2C2F33')

            y_positions = np.arange(len(users) - 1, -1, -1) * 2.0

            for i, y_pos in enumerate(y_positions):
                bg_color = '#36393f' if i % 2 == 0 else '#2f3136'
                rect = plt.Rectangle(
                    (0.2, y_pos - 0.8), 3.6, 1.6,
                    facecolor=bg_color, alpha=0.5, linewidth=2,
                    edgecolor='#7289da' if i < 3 else '#36393f'
                )
                ax.add_patch(rect)

            for i, (user, score, y_pos) in enumerate(zip(users, scores, y_positions)):
                if user:  # Only display if user is still in the server
                    rank_color = '#ffd700' if i < 3 else 'white'
                    plt.text(0.5, y_pos, f"🏆 #{i+1}", fontsize=16, weight='bold', va='center', ha='center', color=rank_color)
                    plt.text(1.5, y_pos, f"{user.name}", fontsize=14, weight='bold', va='center', ha='left', color='white')
                    plt.text(3.5, y_pos, f"Points: {score}", fontsize=14, va='center', ha='right', color='#7289da')

            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            plt.xlim(0, 4)
            plt.ylim(-0.8, max(y_positions) + 0.8 if y_positions.size > 0 else 1)
            plt.title("👑 Leaderboard 👑", pad=20, fontsize=24, color='white', weight='bold')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            plt.close()

            await ctx.send(file=discord.File(buf, "leaderboard.png"))
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            await ctx.send("Error generating leaderboard. Please try again later.")

    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("Shutting down bot...")
        await self.save_points() # Save points before closing
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