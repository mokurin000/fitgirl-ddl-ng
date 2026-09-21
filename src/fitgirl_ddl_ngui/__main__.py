"""Entry point of the fitgirl DDL GUI."""

import wx

import sentry_sdk
from loguru import logger
from importlib.metadata import version
from sentry_sdk.integrations.loguru import LoguruIntegration

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

    sentry_sdk.init(
        dsn="https://283c7a3be770406db49a2e8ea71eb494@app.glitchtip.com/28055",
        release=version("fitgirl-ddl-ng"),
        traces_sample_rate=0.01,
        auto_session_tracking=False,
        integrations=[
            LoguruIntegration(capture_sentry_logs=True),
        ],
        send_default_pii=False,
        _experiments={
            "data_collection": {
                "user_info": False,
                "gen_ai": {"inputs": False, "outputs": False},
            },
        },
    )

    raise Exception()

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
