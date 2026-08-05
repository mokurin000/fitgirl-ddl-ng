import asyncio
from pathlib import Path

import typer
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng import cookies_valid, COOKIES_SESSION
from fitgirl_ddl_ng.extract_ddl import extract_ddl

app = typer.Typer(add_completion=False)


async def export_aria2_input(urls_file: Path):
    if not cookies_valid():
        logger.error("Cookies expired, exiting...")
        raise typer.Exit(code=1)

    if not urls_file.exists():
        logger.error(f"URL file not found: {urls_file}")
        raise typer.Exit(code=1)

    urls = [
        line.strip()
        for line in urls_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not urls:
        logger.error("No URLs found in file")
        raise typer.Exit(code=1)

    logger.info(f"Loaded {len(urls)} URLs")

    browser = await zd.start()

    # Load cookies for fuckingfast
    await browser.cookies.load(COOKIES_SESSION)

    tab = await browser.get("https://fuckingfast.co")
    await tab.wait_for_ready_state("interactive", timeout=60)

    aria2_input = await extract_ddl(tab, urls)
    print(aria2_input)

    await browser.stop()


async def async_main(urls_file: Path):
    await export_aria2_input(urls_file)


@app.command()
def main(
    urls_file: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Text file containing fuckingfast.co URLs",
    ),
):
    asyncio.run(async_main(urls_file))


if __name__ == "__main__":
    app()
