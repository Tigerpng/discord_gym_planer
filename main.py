from bot import Planbot

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Token über Environment Variable setzen

def run():
    bot = Planbot()
    bot.run(TOKEN)

if __name__ == "__main__":
    run()
