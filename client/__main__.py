import asyncio
import os

from dotenv import load_dotenv

from windiafaq.discord.bot import WindiaFAQ


load_dotenv(dotenv_path=".env.client")


async def main():
    await WindiaFAQ("%", os.environ["IPC_ENDPOINT"]).start(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
    