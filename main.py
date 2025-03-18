from flask import Flask
from threading import Thread
import os
import asyncio
import logging
from bot import main  # Import the main function from bot.py

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error in Flask server: {e}")

async def run_bot():
    """Run the Discord bot"""
    try:
        logger.info("Starting Discord bot...")
        await main()  # Run the bot
    except Exception as e:
        logger.error(f"Error in Discord bot: {e}")

def keep_alive():
    """Start the Flask server in a separate thread"""
    try:
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True  # Make thread exit when main thread exits
        flask_thread.start()
        logger.info("Flask server started successfully")
    except Exception as e:
        logger.error(f"Error starting Flask server thread: {e}")

if __name__ == "__main__":
    try:
        # Start the Flask server in a separate thread
        keep_alive()

        # Run the Discord bot in the main thread
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"Critical error in main process: {e}")