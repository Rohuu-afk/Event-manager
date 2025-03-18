import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("BasicCommands cog initialized")

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the cog is ready"""
        logger.info("BasicCommands cog is ready")
        # Log available commands
        commands_list = [cmd.name for cmd in self.bot.commands]
        logger.info(f"Available commands: {', '.join(commands_list)}")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        try:
            latency = round(self.bot.latency * 1000)
            await ctx.send(f'Pong! 🏓 Latency: {latency}ms')
            logger.debug(f"Ping command executed by {ctx.author}. Latency: {latency}ms")
        except Exception as e:
            logger.error(f"Error in ping command: {str(e)}")
            await ctx.send("Error measuring latency")

    @commands.command(name='status')
    async def status(self, ctx):
        """Check bot's status"""
        try:
            embed = discord.Embed(
                title="🤖 Bot Status",
                color=discord.Color.green()
            )
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Latency", value=f"🏓 {round(self.bot.latency * 1000)}ms", inline=True)
            embed.add_field(name="Commands", value=f"📝 {len(self.bot.commands)}", inline=True)
            embed.set_footer(text="Type !help to see all available commands")

            await ctx.send(embed=embed)
            logger.debug(f"Status command executed by {ctx.author}")
        except Exception as e:
            logger.error(f"Error in status command: {str(e)}")
            await ctx.send("Error fetching status")

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
    logger.info("BasicCommands cog added to bot")