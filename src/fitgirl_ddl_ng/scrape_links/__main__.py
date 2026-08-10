import asyncio
from urllib.parse import urlparse

import typer
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng.scrape_links import FuckingFastMissing

FUCKING_FAST = "div.entry-content ul > li:nth-child(2)"

FILE_HOSTER_SINGLE = f"{FUCKING_FAST} > a"
"""For single-link releases it's a fuckingfast.co URL,

otherwise refers to a pastebin for all fuckingfast links."""

FILE_HOSTER_SPOLIER = f"{FUCKING_FAST} > div.su-spoiler > div.su-spoiler-content"
"""Spolier content for multi-part releases."""


async def scrape_ff_links(tab: zd.Tab, url: str) -> list[str]:
    """
    Try to fetch fuckingfast.co links from a fitgirl game post.

    :raise FuckingFastMissing: fuckingfast.co file hoster not found
    """

    logger.info(f"Goto {url}...")

    await tab.get(url)
    await tab.wait_for_ready_state(until="interactive", timeout=60)
    logger.info("Page loaded, scraping...")

    # Sometimes fitgirl put multiple "FileHoster: FuckingFast" in a post
    filehoster_ff_atags = await tab.query_selector_all(FILE_HOSTER_SINGLE)
    filehoster_ff_atags = [
        tag
        for tag in filehoster_ff_atags
        if "Filehoster: FuckingFast"  # filter exactly FuckingFast button
        in tag.text_all
    ]

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
    filehoster_ff_spoliers = await tab.query_selector_all(FILE_HOSTER_SPOLIER)

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


async def main(urls: list[str]):
    browser = await zd.start(config=zd.Config(headless=True))
    tab = await browser.get()

    try:
        for url in urls:
            url = url.strip()
            if not url:
                logger.error("Game url cannot be empty!")
                continue
            if not url.startswith("https://fitgirl-repacks.site/"):
                logger.error("Fake fitgirl website was found!")
                continue

            slug = urlparse(url).path.strip("/")

            try:
                urls = await scrape_ff_links(tab, url)
            except FuckingFastMissing as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue

            file = f"{slug}.txt"
            with open(file, "w", encoding="utf-8") as f:
                print(*urls, sep="\n", file=f)
            logger.info(f"Scraped: {file}")
    finally:
        logger.info("Cleaning up...")
        await browser.stop()


app = typer.Typer(add_completion=False)


@app.command()
def cli(
    urls: list[str] = typer.Argument(
        ...,
        help="FitGirl repack URLs",
    ),
):
    asyncio.run(main(urls))


if __name__ == "__main__":
    app()
