from flask import Flask
from threading import Thread
import os
from bot import main
import asyncio
import logging

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

def run():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error in web server: {e}")

def keep_alive():
    """Start the Flask server in a separate thread"""
    try:
        server = Thread(target=run)
        server.daemon = True  # Make thread exit when main thread exits
        server.start()
        logger.info("Web server started successfully")
    except Exception as e:
        logger.error(f"Error starting web server thread: {e}")

if __name__ == "__main__":
    try:
        # Start the web server in a separate thread
        keep_alive()
        logger.info("Starting Discord bot...")
        # Run the bot in the main thread
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Critical error in main process: {e}")