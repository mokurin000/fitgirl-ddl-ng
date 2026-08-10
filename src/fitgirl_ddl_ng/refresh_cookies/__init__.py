import asyncio

from loguru import logger
from zendriver import Browser, Config
import zendriver as zd

from fitgirl_ddl_ng import COOKIES_SESSION, cookies_valid


async def ensure_cookies(browser: Browser):
    """Refresh cookies of fuckingfast.co, the `browser` must be NOT headless"""
    tab = await browser.get(
        "https://fuckingfast.co/oemaevh39h2t#Skills_and_Raids_--_fitgirl-repacks.site_--_.rar"
    )

    logger.info("Waiting for cloudflare turnstile...")
    await tab.verify_cf(timeout=60.0)
    logger.info("Cloudflare turnstile bypassed")

    button = await tab.select("a.gay-button")
    while True:
        html = await button.get_html()
        if 'style="opacity:0.5;cursor:not-allowed"' not in html:
            logger.info("Download button ready")
            break
        await asyncio.sleep(0.5)

    # Pop-up ads
    await button.click()

    dlpass = None

    while dlpass is None:
        cookies = await browser.cookies.get_all()
        for cookie in cookies:
            if cookie.name == "dlpass":
                logger.info("Cookies refreshed")
                dlpass = cookie.value
        await asyncio.sleep(0.5)


async def refresh_cookies(force: bool):
    """Refresh cookies with a new headed Chrome instance"""
    global BROWSER_INSTANCE

    if not force and cookies_valid():
        logger.warning("Cookies was up-to-date, no refresh needed")
        return

    browser = await zd.start(config=Config(headless=False))
    BROWSER_INSTANCE = browser

    await browser.connection.send(
        zd.cdp.browser.set_download_behavior(
            "deny",
            events_enabled=True,
        )
    )

    await ensure_cookies(browser=browser)
    await browser.cookies.save(
        file=COOKIES_SESSION,
        pattern="(cf_clearance|dlpass)",
    )

    logger.info("Cleaning up...")

    # Clean-up
    await browser.stop()
