from discord.ext import commands
import logging
import traceback
import discord

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("ErrorHandler cog initialized")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found. Use !help to see available commands.")
            logger.debug(f"Command not found: {ctx.message.content}")
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
            logger.debug(f"Missing permissions for {ctx.author}: {error.missing_permissions}")
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param}")
            logger.debug(f"Missing argument in command {ctx.command}: {error.param}")
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument provided. Please check the command usage with !help.")
            logger.debug(f"Bad argument in command {ctx.command}: {error}")
            return

        if isinstance(error, discord.Forbidden):
            await ctx.send("I don't have permission to do that.")
            logger.error(f"Missing bot permissions: {error}")
            return

        # Log unexpected errors
        logger.error(f"Unexpected error in command {ctx.command}: {error}")
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
    logger.info("ErrorHandler cog added to bot")