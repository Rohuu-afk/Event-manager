from discord.ext import commands
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Use !help to see available commands.")
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param}")
            return

        # Log unexpected errors
        logger.error(f"Unexpected error: {error}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        await ctx.send("An unexpected error occurred. Please try again later.")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle non-command errors"""
        logger.error(f"Error in event {event}")
        logger.error(f"Args: {args}")
        logger.error(f"Kwargs: {kwargs}")
        logger.error(f"Traceback: {traceback.format_exc()}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
