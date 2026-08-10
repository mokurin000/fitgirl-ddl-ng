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


def load_urls(urls_file: Path) -> list[str]:
    """Read and clean URLs from a file."""
    return [
        line.strip()
        for line in urls_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


async def export_aria2_input(urls_files: list[Path]):
    if not cookies_valid():
        logger.error("Cookies expired, exiting...")
        raise typer.Exit(code=1)

    # Load and group URLs from every file
    file_groups: list[tuple[Path, dict[str, list[str]]]] = []
    for urls_file in urls_files:
        if not urls_file.exists():
            logger.error(f"URL file not found: {urls_file}")
            raise typer.Exit(code=1)

        urls = load_urls(urls_file)
        if not urls:
            logger.error(f"No URLs found in file: {urls_file}")
            raise typer.Exit(code=1)

        groups = group_urls(urls)
        logger.info(f"Loaded {len(urls)} URLs from {urls_file} ({len(groups)} groups)")
        file_groups.append((urls_file, groups))

    # First: select groups for every file before touching the browser
    selected_plans: list[tuple[Path, list[str]]] = []
    for urls_file, groups in file_groups:
        selected_groups = await select_groups(groups)
        if not selected_groups:
            logger.error(f"No groups selected for {urls_file}, exiting...")
            raise typer.Exit(code=1)

        selected_urls = [url for group in selected_groups for url in groups[group]]
        logger.info(
            f"{urls_file.name}: selected {len(selected_urls)} URLs "
            f"from {len(selected_groups)} groups"
        )
        selected_plans.append((urls_file, selected_urls))

    # Then: start the browser once and crawl each file in order
    browser = await zd.start(config=zd.Config(headless=True))

    # Load cookies for fuckingfast
    await browser.cookies.load(COOKIES_SESSION)

    tab = await browser.get("https://fuckingfast.co")
    await tab.wait_for_ready_state("loading", timeout=60)

    try:
        for urls_file, selected_urls in selected_plans:
            logger.info(f"Extracting {urls_file}...")
            aria2_input = await extract_ddl(
                tab,
                selected_urls,
                out_dir=urls_file.name.removesuffix(".txt"),
            )

            output = urls_file.with_name(f"aria2-{urls_file.name}")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(aria2_input, encoding="utf-8")
            logger.info(f"Written: {output}")
    finally:
        logger.info("Cleaning up...")
        await browser.stop()


async def async_main(urls_files: list[Path]):
    await export_aria2_input(urls_files)


@app.command()
def main(
    urls_files: list[Path] = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="One or more text files containing fuckingfast.co URLs",
    ),
):
    asyncio.run(async_main(urls_files))


if __name__ == "__main__":
    app()
