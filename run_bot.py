import asyncio
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from bot.bot import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped")
        sys.exit(0)
