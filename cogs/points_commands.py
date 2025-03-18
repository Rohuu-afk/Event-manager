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
        logger.info("PointsCommands cog initialized")

    @commands.command(name='rank')
    async def rank(self, ctx, user: discord.Member = None):
        """Display user's rank card or another member's rank card if mentioned"""
        try:
            # If no member is mentioned, use the command author
            target_user = user or ctx.author
            user_id = str(target_user.id)
            points = self.bot.points.get(user_id, 0)

            # Calculate rank
            sorted_points = sorted(self.bot.points.items(), key=lambda x: x[1], reverse=True)
            rank = next((i + 1 for i, (uid, _) in enumerate(sorted_points) if uid == user_id), len(self.bot.points) + 1)

            # Create base image
            img = Image.new('RGBA', (934, 282), (44, 47, 51, 255))  # Discord dark theme background
            draw = ImageDraw.Draw(img)

            # Draw background rectangle
            draw.rectangle((10, 10, 924, 272), fill=(54, 57, 63, 255))

            # Draw avatar circle
            avatar_size = 180
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

            # Get user avatar
            avatar_url = str(target_user.avatar.url) if target_user.avatar else target_user.default_avatar.url
            response = requests.get(avatar_url)
            avatar = Image.open(BytesIO(response.content))
            avatar = avatar.resize((avatar_size, avatar_size))

            # Apply circular mask to avatar
            output = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0))
            output.putalpha(mask)

            # Paste avatar
            img.paste(output, (50, 51), output)

            # Load font with adjusted sizes
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
                normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                title_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()

            # Draw text with emojis
            draw.text((280, 50), "🎮 Event Avenger Rank Card 🎮", fill='white', font=title_font)
            draw.text((280, 100), f"⭐ Points: {points}", fill='white', font=normal_font)
            draw.text((280, 140), f"👑 Rank: #{rank}", fill='white', font=normal_font)

            # Draw invitation text in one line
            draw.text((280, 190), "Make your friends join Event avengers too for fun competition!", 
                     fill=(114, 137, 218), font=normal_font)  # Discord blurple color

            # Save and send
            buffer = BytesIO()
            img.save(buffer, 'PNG')
            buffer.seek(0)

            await ctx.send(file=discord.File(buffer, 'rank_card.png'))
            logger.info(f"Generated rank card for user {target_user.name}")

        except Exception as e:
            logger.error(f"Error generating rank card: {e}")
            await ctx.send("Error generating rank card. Please try again later.")

    @commands.command(name='pointsystem')
    async def pointsystem(self, ctx):
        """Display information about the point system"""
        try:
            # Send point system info as a regular message
            points_info = (
                "📊 **Event Avengers Point System**\n\n"
                "🎯 Point Earnings:\n"
                "• Invites: 8 points (tracked by <@720351927581278219>)\n"
                "• Daily event winning: 10 points\n"
                "• Quick event winning: 30 points\n"
                "• Long event winning: 90 points"
            )

            await ctx.send(points_info)
            logger.info(f"Point system info displayed for user {ctx.author.name}")
        except Exception as e:
            logger.error(f"Error displaying point system info: {e}")
            await ctx.send("Error displaying point system information. Please try again later.")

async def setup(bot):
    await bot.add_cog(PointsCommands(bot))