"""Main window of the fitgirl DDL GUI."""

import re
from concurrent.futures import Future
from typing import TYPE_CHECKING

import wx
from loguru import logger

if TYPE_CHECKING:
    from fitgirl_ddl_ng.gui.worker import GuiWorker

_FITGIRL_URL_RE = re.compile(r"https://fitgirl-repacks\.site/[^/?#\s]+/?")


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
        self.game_gauge = wx.Gauge(panel, range=100)
        self.overall_gauge = wx.Gauge(panel, range=100)
        log_label = wx.StaticText(panel, label="Log:")
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        button_row.Add(self.scrape_button, 0, wx.ALL, 8)
        button_row.Add(
            self.game_gauge,
            1,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.TOP,
            8,
        )

        self._pulse_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_pulse, self._pulse_timer)

        sizer.Add(hint, 0, wx.ALL, 8)
        sizer.Add(self.urls_text, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        sizer.Add(button_row, 0, wx.EXPAND)
        sizer.Add(self.overall_gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
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

    def _on_pulse(self, _event) -> None:
        """Advance the indeterminate per-game bar by one pulse step."""

        self.game_gauge.Pulse()

    def game_progress_start(self) -> None:
        """Begin the indeterminate per-game bar during the prep phase."""

        self._pulse_timer.Start(50)

    def game_progress_range(self, total: int) -> None:
        """Switch the per-game bar to determinate with the given range."""

        self._pulse_timer.Stop()
        self.game_gauge.SetRange(max(1, total))
        self.game_gauge.SetValue(0)

    def game_progress_update(self, done: int) -> None:
        """Set the current per-game extraction step."""

        self.game_gauge.SetValue(done)

    def game_progress_finish(self) -> None:
        """Stop pulsing and reset the per-game bar for the next game."""

        self._pulse_timer.Stop()
        self.game_gauge.SetValue(0)

    def overall_progress(self, total: int, done: int) -> None:
        """Set the overall bar's range and current value."""

        self.overall_gauge.SetRange(max(1, total))
        self.overall_gauge.SetValue(done)

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
