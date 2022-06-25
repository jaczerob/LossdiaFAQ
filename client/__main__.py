import asyncio
import os

from windiafaq.discord.bot import WindiaFAQ


async def main():
    await WindiaFAQ("%", os.environ["TCP_ENDPOINT"]).start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
    