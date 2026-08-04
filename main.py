import asyncio
import queue

import nodriver as uc
from nodriver import cdp

BROWSER_INSTANCE = None
DOWNLOAD_EVENTS = queue.Queue()


def download_handler(event: cdp.browser.DownloadWillBegin):
    print(f"Detected download event: {event.guid}")
    DOWNLOAD_EVENTS.put(event.guid)


async def cancel_downloads():
    while True:
        try:
            guid = DOWNLOAD_EVENTS.get_nowait()
        except queue.Empty:
            await asyncio.sleep(0.0)
        else:
            await BROWSER_INSTANCE.send(cdp.browser.cancel_download(guid))


async def main():
    global BROWSER_INSTANCE

    config = uc.Config()
    browser = await uc.start(config=config)
    BROWSER_INSTANCE = browser

    page = await browser.get(
        "https://fuckingfast.co/oemaevh39h2t#Skills_and_Raids_--_fitgirl-repacks.site_--_.rar"
    )

    await page.wait_for("div#cf-turnstile", timeout=30.0)
    await page.verify_cf()

    button = await page.select("a.gay-button")
    while True:
        html = await button.get_html()
        if 'style="opacity:0.5;cursor:not-allowed"' not in html:
            break
        await asyncio.sleep(0.5)

    print("Button available now!")

    browser.add_handler(
        cdp.browser.DownloadWillBegin,
        download_handler,
    )

    # Pop-up ads
    await button.click()

    await asyncio.sleep(180.0)


if __name__ == "__main__":
    asyncio.run(main())
