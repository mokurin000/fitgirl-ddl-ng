"""A wxPython GUI wrapping the fitgirl-ddl-ng pipeline."""

import asyncio
import re
import threading
from concurrent.futures import Future
from pathlib import Path
from urllib.parse import urlparse

import wx
import zendriver as zd
from loguru import logger

from fitgirl_ddl_ng.extract_ddl import DEFAULT_SELECT_MARKERS, extract_ddl, group_urls
from fitgirl_ddl_ng.refresh_cookies import refresh_cookies
from fitgirl_ddl_ng.scrape_links import FuckingFastMissing, scrape_ff_links

_FITGIRL_URL_RE = re.compile(r"https://fitgirl-repacks\.site/[^/?#\s]+/?")
_FUCKING_FAST = "https://fuckingfast.co"


def validate_fitgirl_urls(text: str) -> list[str]:
    """
    Parse a block of text into valid fitgirl-repacks.site URLs.

    :param text: the multiline input, one URL per line
    :return: the valid URLs found in the text
    :raise ValueError: when any non-empty line is not a valid fitgirl URL
    """

    valid = []
    invalid = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if _FITGIRL_URL_RE.fullmatch(line):
            valid.append(line)
        else:
            invalid.append(line)

    if invalid:
        raise ValueError("\n".join(invalid))

    return valid


def slug_from(url: str) -> str:
    """
    Extract the game slug from a fitgirl-repacks.site URL.

    :param url: a validated fitgirl URL
    :return: the slug used for the output file and the out= directory
    """

    return urlparse(url).path.strip("/")


class GroupSelectDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, slug: str, groups: list[str]) -> None:
        """
        Ask the user which download groups to keep for a game.

        :param parent: the parent window
        :param slug: the game slug shown in the title
        :param groups: the group names to choose from
        """

        super().__init__(parent, title=f"Select groups — {slug}", size=(520, 420))

        hint = wx.StaticText(self, label="Groups found for this game:")
        self.list = wx.CheckListBox(self, choices=groups)
        for index, group in enumerate(groups):
            if any(marker in group for marker in DEFAULT_SELECT_MARKERS):
                self.list.Check(index)

        buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK), id=wx.ID_OK)
        self.Bind(
            wx.EVT_BUTTON,
            lambda _event: self.EndModal(wx.ID_CANCEL),
            id=wx.ID_CANCEL,
        )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hint, 0, wx.ALL, 8)
        sizer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(sizer)

    def get_selection(self) -> list[str]:
        """
        Return the groups the user kept.

        :return: the selected group names
        """

        return [
            self.list.GetString(index)
            for index in range(self.list.GetCount())
            if self.list.IsChecked(index)
        ]


class MainFrame(wx.Frame):
    def __init__(self, worker: "GuiWorker") -> None:
        """
        The main window of the fitgirl DDL GUI.

        :param worker: the background worker running the pipeline
        """

        super().__init__(None, title="Fitgirl DDL", size=(720, 600))
        self.worker = worker
        self.worker.frame = self

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        hint = wx.StaticText(panel, label="fitgirl-repacks.site URLs, one per line:")
        self.urls_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
        self.urls_text.SetHint("https://fitgirl-repacks.site/<game-slug>/")
        self.scrape_button = wx.Button(panel, label="Scrape")
        log_label = wx.StaticText(panel, label="Log:")
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        sizer.Add(hint, 0, wx.ALL, 8)
        sizer.Add(self.urls_text, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        sizer.Add(self.scrape_button, 0, wx.ALL, 8)
        sizer.Add(log_label, 0, wx.LEFT | wx.RIGHT, 8)
        sizer.Add(self.log_text, 3, wx.EXPAND | wx.ALL, 8)
        panel.SetSizer(sizer)

        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Ready")

        self.scrape_button.Bind(wx.EVT_BUTTON, self.on_scrape)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def append_log(self, text: str) -> None:
        """Append a line to the log pane."""

        self.log_text.AppendText(f"{text}\n")

    def set_running(self, running: bool) -> None:
        """Enable or disable the controls while the pipeline is running."""

        self.scrape_button.Enable(not running)
        self.status_bar.SetStatusText("Working..." if running else "Ready")

    def bring_to_front(self) -> None:
        """Raise the window and give it keyboard focus."""

        self.Raise()
        self.SetFocus()

    def schedule_focus_restore(self) -> None:
        """Re-raise the window once Chrome has stopped stealing focus."""

        wx.CallLater(1500, self.bring_to_front)

    def on_scrape(self, _event) -> None:
        """Start the pipeline for the URLs in the input box."""

        try:
            urls = validate_fitgirl_urls(self.urls_text.GetValue())
        except ValueError as exc:
            wx.MessageBox(
                f"The following lines are not valid fitgirl URLs:\n\n{exc}",
                "Invalid input",
                wx.OK | wx.ICON_ERROR,
            )
            return

        self.set_running(True)
        future = self.worker.submit(self.worker.run_pipeline(urls))
        future.add_done_callback(lambda done: wx.CallAfter(self.on_pipeline_done, done))

    def on_pipeline_done(self, future: Future) -> None:
        """Re-enable the controls once the pipeline has finished."""

        self.set_running(False)
        try:
            future.result()
        except Exception as exc:
            logger.error(f"Pipeline failed: {exc}")
            wx.MessageBox(str(exc), "Error", wx.OK | wx.ICON_ERROR)

    def on_close(self, event) -> None:
        """Stop the worker before the window closes."""

        self.worker.stop()
        event.Skip()


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
        for url in urls:
            slug = slug_from(url)
            try:
                await self._run_game(url, slug)
            except FuckingFastMissing:
                logger.warning(f"{slug}: fuckingfast.co mirror not available, skipped")
            except Exception:
                logger.exception(f"{slug}: failed")

    async def _ensure_browser(self) -> None:
        """Start the shared browser and a tab on first use."""

        if self._browser is None:
            logger.info("Starting Chrome...")
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

        logger.info(f"{slug}: scraping links...")
        ff_links = await scrape_ff_links(self._tab, url)
        logger.info(f"{slug}: found {len(ff_links)} link(s)")

        logger.info(
            f"{slug}: refreshing cookies, complete the Cloudflare check in Chrome"
        )
        await refresh_cookies(force=True, browser=self._browser)

        groups = group_urls(ff_links)
        selected = await self._ask_group_selection(slug, groups)
        if selected is None:
            logger.info(f"{slug}: skipped by user")
            return

        chosen = [link for group in selected for link in groups[group]]
        logger.info(f"{slug}: extracting direct links...")

        await self._tab.get(_FUCKING_FAST)
        await self._tab.wait_for_ready_state(until="complete", timeout=60.0)
        text = await extract_ddl(self._tab, chosen, out_dir=slug)

        out_file = Path.cwd() / "aria2" / f"{slug}.txt"
        out_file.parent.mkdir(exist_ok=True)
        out_file.write_text(text, encoding="utf-8")
        logger.info(f"{slug}: saved {out_file}")

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
