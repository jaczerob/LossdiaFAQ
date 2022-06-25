import asyncio
import os

from windiafaq import static
from windiafaq.discord.bot import WindiaFAQ


async def main():
    await WindiaFAQ(static.BOT_PREFIX, os.environ["SERVER_CONNECT_URI"]).start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
    