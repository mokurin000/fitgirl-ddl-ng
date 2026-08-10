import asyncio
from urllib.parse import urlparse

import typer
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng.scrape_links import FuckingFastMissing, scrape_ff_links


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
