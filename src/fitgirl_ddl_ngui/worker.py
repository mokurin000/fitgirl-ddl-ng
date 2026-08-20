"""Background pipeline worker for the fitgirl DDL GUI."""

import asyncio
import threading
from concurrent.futures import Future
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import wx
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng.extract_ddl import extract_ddl, group_urls
from fitgirl_ddl_ng.refresh_cookies import refresh_cookies
from fitgirl_ddl_ng.scrape_links import FuckingFastMissing, scrape_ff_links
from fitgirl_ddl_ngui.ui.group_dialog import GroupSelectDialog

if TYPE_CHECKING:
    from fitgirl_ddl_ngui.ui.main_frame import MainFrame

_FUCKING_FAST = "https://fuckingfast.co"


def slug_from(url: str) -> str:
    """
    Extract the game slug from a fitgirl-repacks.site URL.

    :param url: a validated fitgirl URL
    :return: the slug used for the output file and the out= directory
    """

    return urlparse(url).path.strip("/")


class GuiWorker(threading.Thread):
    def __init__(self) -> None:
        """
        Run the async pipeline on a background thread with a single browser.

        :return: None
        """

        super().__init__(daemon=True)
        self.frame: MainFrame | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._browser: zd.Browser | None = None
        self._tab: zd.Tab | None = None

        self._cookies_initialized = False

    def run(self) -> None:
        """Entry point of the background thread."""

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro) -> Future:
        """
        Schedule a coroutine on the worker's event loop.

        :param coro: the coroutine to run
        :return: a future resolving with the coroutine's result
        """

        assert self._loop is not None
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self) -> None:
        """Stop the worker thread and close its browser."""

        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._shutdown(), self._loop)

    async def run_pipeline(self, urls: list[str]) -> None:
        """
        Scrape, refresh cookies, select groups and extract DDL for each URL.

        :param urls: the validated fitgirl URLs to process
        :return: None
        """

        await self._ensure_browser()
        total = len(urls)
        if self.frame is not None:
            wx.CallAfter(self.frame.overall_progress, total, 0)
        for index, url in enumerate(urls, start=1):
            slug = slug_from(url)
            try:
                await self._run_game(url, slug)
            except FuckingFastMissing:
                logger.warning(f"{slug}: fuckingfast.co mirror not available, skipped")
            except Exception:
                logger.exception(f"{slug}: failed")
            finally:
                if self.frame is not None:
                    wx.CallAfter(self.frame.game_progress_finish)
                    wx.CallAfter(self.frame.overall_progress, total, index)

    async def _ensure_browser(self) -> None:
        """Start the shared browser and a tab on first use."""

        if self._browser is None or self._browser.stopped:
            logger.info("Starting Chrome...")

            # Spawning new session would invalidate cookies
            self._cookies_initialized = False
            self._browser = await zd.start(config=zd.Config(headless=False))

            await self._browser.connection.send(
                zd.cdp.browser.set_download_behavior(
                    "deny",
                    events_enabled=True,
                )
            )
            self._tab = await self._browser.get("about:blank")
            self._grab_focus_back()

    def _grab_focus_back(self) -> None:
        """Bring the main window back to the foreground after Chrome starts."""

        if self.frame is None:
            return
        wx.CallAfter(self.frame.bring_to_front)
        wx.CallAfter(self.frame.schedule_focus_restore)

    async def _run_game(self, url: str, slug: str) -> None:
        """Process a single fitgirl URL end to end."""

        if self.frame is not None:
            wx.CallAfter(self.frame.game_progress_start)

        logger.info(f"{slug}: scraping links...")
        ff_links = await scrape_ff_links(self._tab, url)
        logger.info(f"{slug}: found {len(ff_links)} link(s)")

        logger.info(
            f"{slug}: refreshing cookies, complete the Cloudflare check in Chrome"
        )

        await refresh_cookies(
            force=not self._cookies_initialized,
            browser=self._browser,
        )
        self._cookies_initialized = True

        groups = group_urls(ff_links)
        selected = await self._ask_group_selection(slug, groups)
        if selected is None:
            logger.info(f"{slug}: skipped by user")
            return

        chosen = [link for group in selected for link in groups[group]]
        if self.frame is not None:
            wx.CallAfter(self.frame.game_progress_range, len(chosen))
        logger.info(f"{slug}: extracting direct links...")

        await self._tab.get(_FUCKING_FAST)
        await self._tab.wait_for_ready_state(until="complete", timeout=60.0)
        text = await extract_ddl(
            self._tab,
            chosen,
            out_dir=slug,
            progress=self._on_extract_progress,
        )

        out_file = Path.cwd() / "aria2" / f"{slug}.txt"
        out_file.parent.mkdir(exist_ok=True)
        out_file.write_text(text, encoding="utf-8")
        logger.info(f"{slug}: saved {out_file}")

    def _on_extract_progress(self, done: int, _total: int) -> None:
        """Forward per-URL extraction progress to the UI thread."""

        if self.frame is not None:
            wx.CallAfter(self.frame.game_progress_update, done)

    async def _ask_group_selection(
        self, slug: str, groups: dict[str, list[str]]
    ) -> list[str] | None:
        """
        Ask the user which groups to keep, on the UI thread.

        :param slug: the game slug shown in the dialog
        :param groups: the URL groups found for the game
        :return: the selected group names, or None if the user cancelled
        """

        group_names = list(groups)
        if len(group_names) == 1:
            return group_names

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def show_dialog() -> None:
            dialog = GroupSelectDialog(None, slug, group_names)
            if dialog.ShowModal() == wx.ID_OK:
                loop.call_soon_threadsafe(future.set_result, dialog.get_selection())
            else:
                loop.call_soon_threadsafe(future.set_result, None)
            dialog.Destroy()

        wx.CallAfter(show_dialog)
        return await future

    async def _shutdown(self) -> None:
        """Close the browser and stop the event loop."""

        if self._browser is not None:
            await self._browser.stop()
        if self._loop is not None:
            self._loop.stop()
