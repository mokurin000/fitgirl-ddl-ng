import asyncio

import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng import cookies_valid, COOKIES_SESSION


async def export_aria2_input():
    if not cookies_valid():
        logger.error("Cookies expired, exiting...")
        exit(1)

    browser = await zd.start()

    # Load cookies for fuckingfast
    await browser.cookies.load(COOKIES_SESSION)


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
