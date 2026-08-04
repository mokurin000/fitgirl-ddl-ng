import queue
import shutil
import asyncio
import tempfile
from pathlib import Path

import nodriver as uc
from nodriver import Browser, cdp

BROWSER_INSTANCE = None
DOWNLOAD_EVENTS = queue.Queue()

TEMP_DIR = str(Path(tempfile.gettempdir()) / "fitgirl-ddl-ng")


def download_handler(event: cdp.browser.DownloadWillBegin):
    DOWNLOAD_EVENTS.put(event)


async def cancel_downloads():
    while True:
        try:
            event: cdp.browser.DownloadWillBegin = DOWNLOAD_EVENTS.get_nowait()
        except queue.Empty:
            await asyncio.sleep(0.0)
        else:
            await BROWSER_INSTANCE.send(cdp.browser.cancel_download(event.guid))


async def ensure_cookies(browser: Browser):
    page = await browser.get(
        "https://fuckingfast.co/oemaevh39h2t#Skills_and_Raids_--_fitgirl-repacks.site_--_.rar"
    )
    await page.verify_cf(template_image="cloudflare.png")

    button = await page.select("a.gay-button")
    while True:
        html = await button.get_html()
        if 'style="opacity:0.5;cursor:not-allowed"' not in html:
            break
        await asyncio.sleep(0.5)

    # Pop-up ads
    await button.click()

    cf_clearance = None
    dlpass = None

    while dlpass is None:
        cookies = await browser.cookies.get_all()
        for cookie in cookies:
            if cookie.name == "dlpass":
                dlpass = cookie.value
            elif cookie.name == "cf_clearance":
                cf_clearance = cookie.value
        await asyncio.sleep(0.5)

    return f"cf_clearance={cf_clearance}; dlpass={dlpass}"


async def main():
    global BROWSER_INSTANCE

    browser = await uc.start()
    BROWSER_INSTANCE = browser

    asyncio.create_task(cancel_downloads())
    await browser.send(
        cdp.browser.set_download_behavior(
            behavior="allowAndName",
            download_path=TEMP_DIR,
            events_enabled=True,
        )
    )
    browser.add_handler(
        cdp.browser.DownloadWillBegin,
        download_handler,
    )

    cookies = await ensure_cookies(browser=browser)
    print(cookies)

    # Clean-up
    browser.stop()
    print(TEMP_DIR)
    shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
    asyncio.run(main())
