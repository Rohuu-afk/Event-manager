from flask import Flask
from threading import Thread
import os
from bot import main
import asyncio

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    server = Thread(target=run)
    server.start()

if __name__ == "__main__":
    # Start the web server in a separate thread
    keep_alive()
    # Run the bot in the main thread
    asyncio.run(main())
