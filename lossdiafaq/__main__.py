import argparse
import asyncio

import yaml

from lossdiafaq.client import LossdiaFAQ


async def main(test: bool):
    with open('lossdia.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if test:
        token = config["test"]["token"]
        prefix = config["test"]["prefix"]
    else:
        token = config["prod"]["token"]
        prefix = config["prod"]["prefix"]

    async with LossdiaFAQ(prefix) as client:
        await client.start(token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    asyncio.run(main(args.test))