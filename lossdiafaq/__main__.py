import asyncio
import os

from lossdiafaq import static
from lossdiafaq.client import LossdiaFAQ


async def main():
    async with LossdiaFAQ(static.BOT_PREFIX) as client:
        await client.start(os.environ["DISCORD_BOT_TOKEN"])


if __name__ == '__main__':
    asyncio.run(main())