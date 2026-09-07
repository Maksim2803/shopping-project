from bot.bot import Bot
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

if __name__ == "__main__":
    bot = Bot(TOKEN)
    bot.start()