import shutil
import asyncio
import tempfile
from pathlib import Path

import zendriver as zd
from zendriver import Browser, cdp

BROWSER_INSTANCE = None

TEMP_DIR = str(Path(tempfile.gettempdir()) / "fitgirl-ddl-ng")


async def download_handler(event: cdp.browser.DownloadWillBegin):
    await BROWSER_INSTANCE.connection.send(cdp.browser.cancel_download(event.guid))


async def ensure_cookies(browser: Browser):
    page = await browser.get(
        "https://fuckingfast.co/oemaevh39h2t#Skills_and_Raids_--_fitgirl-repacks.site_--_.rar"
    )
    await page.verify_cf()

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

    browser = await zd.start()
    BROWSER_INSTANCE = browser

    await browser.connection.send(
        cdp.browser.set_download_behavior(
            behavior="allowAndName",
            download_path=TEMP_DIR,
            events_enabled=True,
        )
    )
    browser.connection.add_handler(
        cdp.browser.DownloadWillBegin,
        download_handler,
    )

    cookies = await ensure_cookies(browser=browser)
    print(cookies)

    # Clean-up
    await browser.stop()
    shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
    asyncio.run(main())
