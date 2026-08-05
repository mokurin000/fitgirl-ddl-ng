import asyncio
from urllib.parse import urlparse

import zendriver as zd
from loguru import logger
from prompt_toolkit.shortcuts import PromptSession

from fitgirl_ddl_ng import COOKIES_SESSION, cookies_valid
from fitgirl_ddl_ng.scrape_links import FuckingFastMissing

FUCKING_FAST = "div.entry-content ul > li:nth-child(2)"

FILE_HOSTER_SINGLE = f"{FUCKING_FAST} > a"
"""For single-link releases it's a fuckingfast.co URL,

otherwise refers to a pastebin for all fuckingfast links."""

FILE_HOSTER_SPOLIER = f"{FUCKING_FAST} > div.su-spoiler > div.su-spoiler-content"
"""Spolier content for multi-part releases."""


async def scrape_ff_links(tab: zd.Tab) -> list[str]:
    """
    Try to fetch fuckingfast.co links from a fitgirl game post.

    :raise FuckingFastMissing: fuckingfast.co file hoster not found
    """

    logger.info(f"Processing {tab.url}...")

    await tab.wait_for_ready_state(until="interactive")
    logger.info("Page loaded, scraping...")

    # Sometimes fitgirl put multiple "FileHoster: FuckingFast" in a post
    filehoster_ff_atags = await tab.select_all(FILE_HOSTER_SINGLE)

    match len(filehoster_ff_atags):
        case 0:
            raise FuckingFastMissing()
        case 1:
            pass
        case _:
            logger.warning(
                "Found multiple 'FileHoster: FuckingFast', picking the first"
            )

    filehoster_ff_a = filehoster_ff_atags.pop(0)
    filehoster_ff_spoliers = await tab.select_all(FILE_HOSTER_SPOLIER)

    if not filehoster_ff_spoliers:
        single_url = filehoster_ff_a.attrs.get("href")
        if single_url is None:
            raise FuckingFastMissing()
        return [single_url]
    else:
        spoliter_count = len(filehoster_ff_spoliers)
        if spoliter_count > 1:
            logger.warning("Found multiple ff links spoliers")

        urls = []

        # https://fitgirl-repacks.site/honey-select-2-libido/
        # Some repacks have multiple sections with different spolier blocks
        for spolier in filehoster_ff_spoliers:
            atags = await spolier.query_selector_all("a")
            for tag in atags:
                item_url = tag.attrs.get("href")
                if item_url is None:
                    logger.warning()
                    continue
                urls.append(item_url)

        return sorted(set(urls), key=lambda url: url.split("#")[1])


async def main():
    if not cookies_valid():
        logger.error("Cookies expired, exiting...")
        exit(1)

    session = PromptSession()

    url: str = await session.prompt_async(
        message="Game to scrape: ",
        placeholder="https://fitgirl-repacks.site/.../",
    )

    if not url.startswith("https://fitgirl-repacks.site/"):
        logger.error("Fake fitgirl website was found!")
        exit(1)

    slug = urlparse(url).path.strip("/")

    browser = await zd.start()

    # Load cookies for fuckingfast
    await browser.cookies.load(COOKIES_SESSION)

    tab = await browser.get(url)
    urls = await scrape_ff_links(tab)

    with open(f"{slug}.txt", "w", encoding="utf-8") as f:
        print(*urls, sep="\n", file=f)

    await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
