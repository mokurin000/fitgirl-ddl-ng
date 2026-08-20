"""Entry point of the fitgirl DDL GUI."""

import wx

from loguru import logger

from fitgirl_ddl_ngui import GuiWorker, MainFrame


def make_log_sink(frame: MainFrame):
    def sink(message) -> None:
        wx.CallAfter(frame.append_log, str(message).rstrip())

    return sink


def main() -> None:
    """
    Launch the fitgirl DDL GUI.

    :return: None
    """

    app = wx.App()
    # Enable the dark mode support on Windows
    if hasattr(app, "MSWEnableDarkMode"):
        app.MSWEnableDarkMode(wx.App.DarkMode_Auto)

    worker = GuiWorker()
    frame = MainFrame(worker)
    logger.add(
        make_log_sink(frame),
        enqueue=True,
        format="{time:HH:mm:ss} {level:<8} {message}",
    )
    frame.Centre()
    frame.Show()
    worker.start()
    app.MainLoop()
    worker.stop()


if __name__ == "__main__":
    main()
