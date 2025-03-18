import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        try:
            latency = round(self.bot.latency * 1000)
            await ctx.send(f'Pong! Latency: {latency}ms')
            logger.debug(f"Ping command executed. Latency: {latency}ms")
        except Exception as e:
            logger.error(f"Error in ping command: {str(e)}")
            await ctx.send("Error measuring latency")

    @commands.command(name='status')
    async def status(self, ctx):
        """Check bot's status"""
        try:
            embed = discord.Embed(
                title="Bot Status",
                color=discord.Color.green()
            )
            embed.add_field(name="Uptime", value="Online", inline=True)
            embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
            await ctx.send(embed=embed)
            logger.debug("Status command executed successfully")
        except Exception as e:
            logger.error(f"Error in status command: {str(e)}")
            await ctx.send("Error fetching status")

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
