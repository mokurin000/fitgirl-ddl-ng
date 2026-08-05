import asyncio
from pathlib import Path

import typer
import questionary
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng import cookies_valid, COOKIES_SESSION
from fitgirl_ddl_ng.extract_ddl import extract_ddl, group_urls

app = typer.Typer(add_completion=False)

DEFAULT_SELECT_MARKERS = ("fitgirl-repacks.site", "FIXED")
"""Group names containing any marker are pre-selected in the selection prompt."""


async def select_groups(groups: dict[str, list[str]]) -> list[str]:
    """Pick which URL groups to extract, pre-selecting the obvious ones."""
    if len(groups) == 1:
        return list(groups)

    choices = [
        questionary.Choice(
            title=name,
            value=name,
            checked=any(marker in name for marker in DEFAULT_SELECT_MARKERS),
        )
        for name in groups
    ]
    selected = await questionary.checkbox(
        "Select groups to extract", choices=choices
    ).ask_async()
    return selected or []


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

    groups = group_urls(urls)
    selected_groups = await select_groups(groups)
    if not selected_groups:
        logger.error("No groups selected, exiting...")
        raise typer.Exit(code=1)

    selected_urls = [url for group in selected_groups for url in groups[group]]
    logger.info(
        f"Selected {len(selected_urls)} URLs from {len(selected_groups)} groups"
    )

    browser = await zd.start()

    # Load cookies for fuckingfast
    await browser.cookies.load(COOKIES_SESSION)

    tab = await browser.get("https://fuckingfast.co")
    await tab.wait_for_ready_state("interactive", timeout=60)

    aria2_input = await extract_ddl(tab, selected_urls)

    output = urls_file.with_name(f"aria2-{urls_file.name}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(aria2_input, encoding="utf-8")
    logger.info(f"Written: {output}")

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
