import asyncio

import yaml

from lossdiafaq.client import LossdiaFAQ


async def main():
    with open('lossdia.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    async with LossdiaFAQ() as client:
        await client.start(config["token"])


if __name__ == '__main__':
    asyncio.run(main())