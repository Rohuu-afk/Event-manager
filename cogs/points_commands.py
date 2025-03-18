import discord
from discord.ext import commands
import logging
import matplotlib.pyplot as plt
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

class PointsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='rank')
    async def rank(self, ctx):
        """Display user's rank card"""
        try:
            # Get user data
            user_id = str(ctx.author.id)
            points = self.bot.points.get(user_id, 0)

            # Calculate rank
            sorted_points = sorted(self.bot.points.items(), key=lambda x: x[1], reverse=True)
            rank = next((i + 1 for i, (uid, _) in enumerate(sorted_points) if uid == user_id), len(self.bot.points) + 1)

            # Create base image
            img = Image.new('RGBA', (934, 282), (44, 47, 51, 255))  # Discord dark theme background
            draw = ImageDraw.Draw(img)

            # Draw background rectangle
            draw.rectangle((10, 10, 924, 272), fill=(54, 57, 63, 255))

            # Load and paste user avatar
            avatar_size = 180
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

            # Get user avatar
            avatar_url = str(ctx.author.avatar.url) if ctx.author.avatar else ctx.author.default_avatar.url
            response = requests.get(avatar_url)
            avatar = Image.open(BytesIO(response.content))
            avatar = avatar.resize((avatar_size, avatar_size))

            # Apply circular mask to avatar
            output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0))
            output.putalpha(mask)

            # Paste avatar
            img.paste(output, (50, 51), output)

            # Load font
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
            except:
                title_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()

            # Draw text
            draw.text((280, 30), "Event Avenger rank card", fill='white', font=title_font)
            draw.text((280, 120), f"Points: {points}", fill='white', font=normal_font)
            draw.text((280, 170), f"Rank: #{rank}", fill='white', font=normal_font)
            draw.text((280, 220), "Make your friends join Event avengers too for fun competition!", 
                     fill=(114, 137, 218), font=normal_font)  # Discord blurple color

            # Save and send
            buffer = BytesIO()
            img.save(buffer, 'PNG')
            buffer.seek(0)

            await ctx.send(file=discord.File(buffer, 'rank_card.png'))
            logger.info(f"Generated rank card for user {ctx.author.name}")

        except Exception as e:
            logger.error(f"Error generating rank card: {e}")
            await ctx.send("Error generating rank card. Please try again later.")

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx):
        """Display the points leaderboard"""
        try:
            sorted_points = sorted(self.bot.points.items(), key=lambda x: x[1], reverse=True)[:10]
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
            logger.info(f"Generated leaderboard for server {ctx.guild.name}")

        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            await ctx.send("Error generating leaderboard. Please try again later.")

    @commands.command(name='addpoints')
    @commands.has_permissions(administrator=True)
    async def addpoints(self, ctx, user: discord.Member, amount: int):
        """Add points to a user (Admin only)"""
        try:
            user_id = str(user.id)
            self.bot.points[user_id] = self.bot.points.get(user_id, 0) + amount
            await self.bot.save_points()
            await ctx.send(f"Added {amount} points to {user.display_name}. Total points: {self.bot.points[user_id]}")
            logger.info(f"Added {amount} points to user {user.name}")
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            await ctx.send("Error adding points. Please try again later.")

    @commands.command(name='removepoints')
    @commands.has_permissions(administrator=True)
    async def removepoints(self, ctx, user: discord.Member, amount: int):
        """Remove points from a user (Admin only)"""
        try:
            user_id = str(user.id)
            self.bot.points[user_id] = max(0, self.bot.points.get(user_id, 0) - amount)
            await self.bot.save_points()
            await ctx.send(f"Removed {amount} points from {user.display_name}. Total points: {self.bot.points[user_id]}")
            logger.info(f"Removed {amount} points from user {user.name}")
        except Exception as e:
            logger.error(f"Error removing points: {e}")
            await ctx.send("Error removing points. Please try again later.")

async def setup(bot):
    await bot.add_cog(PointsCommands(bot))