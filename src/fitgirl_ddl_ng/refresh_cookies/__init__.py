import asyncio

from loguru import logger
from zendriver import Browser, Config, Tab
from zendriver.cdp.runtime import BindingCalled
import zendriver as zd

from fitgirl_ddl_ng import COOKIES_SESSION, cookies_valid


async def log_xhr_requests(tab: Tab):
    async def on_log(event: BindingCalled):
        logger.info(event.payload)

    await tab.send(zd.cdp.runtime.add_binding(name="pythonLog"))

    tab.add_handler(
        BindingCalled,
        on_log,
    )

    await tab.evaluate("""
(() => {
    const oldOpen = XMLHttpRequest.prototype.open;
    const oldSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this.__log_url = url;
        this.__log_method = method;
        return oldOpen.call(this, method, url, ...args);
    };

    XMLHttpRequest.prototype.send = function(body) {
        if (this.__log_url?.includes("/f/")) {
            pythonLog(
                `[XHR] ${this.__log_method} ${this.__log_url}`
            );
        }

        this.addEventListener("load", () => {
            if (this.__log_url?.includes("/f/")) {
                pythonLog(
                    `[XHR] ${this.__log_method} ${this.__log_url} -> ${this.status}`
                );
            }
        });

        return oldSend.call(this, body);
    };
})();
""")


async def ensure_cookies(browser: Browser):
    """Refresh cookies of fuckingfast.co, the `browser` must be NOT headless"""
    # Force refreshing cookies from a clean state
    await browser.cookies.clear()

    tab = await browser.get(
        "https://fuckingfast.co/oemaevh39h2t#Skills_and_Raids_--_fitgirl-repacks.site_--_.rar"
    )
    await tab.wait_for_ready_state(until="complete", timeout=60)

    logger.info("Waiting for cloudflare turnstile...")
    await tab.verify_cf(timeout=60.0)
    logger.info("Cloudflare turnstile bypassed")

    button = await tab.select("a.gay-button")
    while True:
        html = await button.get_html()
        if 'style="opacity:0.5;cursor:not-allowed"' not in html:
            logger.info("Download button highlighted")
            break
        await asyncio.sleep(0.1)
    logger.info("Waiting for 1s for button really operable")
    await asyncio.sleep(1.0)

    # Pop-up ads
    await log_xhr_requests(tab)
    await button.click()
    logger.info("Button clicked, waiting for event...")
    logger.info("Should have '[XHR]', otherwise report a bug!")

    dlpass = None

    while dlpass is None:
        cookies = await browser.cookies.get_all()
        for cookie in cookies:
            if cookie.name == "dlpass":
                logger.info("Cookies refreshed")
                dlpass = cookie.value
        await asyncio.sleep(0.5)


async def refresh_cookies(force: bool, browser: Browser | None = None):
    """
    Refresh cookies of fuckingfast.co so direct links can be extracted.

    :param force: refresh even when the stored cookies are still valid
    :param browser: an existing headed browser to reuse, or None to start one
    :return: None
    """

    if not force and cookies_valid():
        logger.warning("Cookies was up-to-date, no refresh needed")
        return

    owns_browser = browser is None
    if owns_browser:
        browser = await zd.start(config=Config(headless=False))

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

    if owns_browser:
        logger.info("Cleaning up...")
        await browser.stop()
