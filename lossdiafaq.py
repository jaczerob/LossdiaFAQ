import argparse
import asyncio
import sys

import yaml

from lossdiafaq.client import LossdiaFAQ


async def main(test: bool):
    with open('lossdia.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if test:
        token = config["test"]["token"]
    else:
        token = config["prod"]["token"]

    async with LossdiaFAQ() as client:
        await client.start(token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    asyncio.run(main(args.test))