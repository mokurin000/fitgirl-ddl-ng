from loguru import logger
import zendriver as zd


class FuckingFastMissing(Exception):
    def __str__(self):
        return "fuckingfast.co mirror not available"


FUCKING_FAST = "div.entry-content ul > li:nth-child(2)"

FILE_HOSTER_SINGLE = f"{FUCKING_FAST} > a"
"""For single-link releases it's a fuckingfast.co URL,

otherwise refers to a pastebin for all fuckingfast links."""

SPOLIER_ATAGS = "div.su-spoiler > div.su-spoiler-content > a"
"""Spolier content for multi-part releases."""


async def scrape_ff_links(tab: zd.Tab, url: str) -> list[str]:
    """
    Try to fetch fuckingfast.co links from a fitgirl game post.

    :raise FuckingFastMissing: fuckingfast.co file hoster not found
    """

    logger.info(f"Goto {url}...")

    await tab.get(url)
    await tab.wait_for("article.post", timeout=120)

    try:
        await tab.wait_for(FILE_HOSTER_SINGLE, timeout=10)
    except TimeoutError:
        raise FuckingFastMissing()
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
    spolier_atags = await tab.query_selector_all(SPOLIER_ATAGS)

    if not spolier_atags:
        single_url = filehoster_ff_a.attrs.get("href")
        if single_url is None:
            raise FuckingFastMissing()
        return [single_url]
    else:
        urls = []

        # https://fitgirl-repacks.site/honey-select-2-libido/
        # Some repacks have multiple sections with different spolier blocks
        for tag in spolier_atags:
            item_url: str = tag.attrs.get("href")
            if item_url is None:
                logger.warning("Missing spolier link: fitgirl side bug!")
                continue
            # Filter out non-fuckingfast urls
            if not item_url.startswith("https://fuckingfast.co/"):
                continue
            urls.append(item_url)

        return sorted(set(urls), key=lambda url: url.split("#")[1])
