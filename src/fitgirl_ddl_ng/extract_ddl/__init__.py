import re
from urllib.parse import urlparse

from zendriver import Tab
from loguru import logger

try:
    from tqdm.asyncio import tqdm

    _HAS_TQDM = True
except ImportError, ModuleNotFoundError:
    _HAS_TQDM = False
else:
    logger.remove()  # Remove default handler
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

_SUFFIX_PATTERN = re.compile(r"\.part\d+\.rar$|\.rar$")


def group_urls(urls: list[str]) -> dict[str, list[str]]:
    """Group URLs by their fragment."""

    groups: dict[str, list[str]] = {}
    for url in urls:
        fragment = urlparse(url).fragment
        if fragment and _SUFFIX_PATTERN.search(fragment):
            group = _SUFFIX_PATTERN.sub("", fragment)
        else:
            group = fragment
        groups.setdefault(group, []).append(url)
    return groups


async def extract_ddl(tab: Tab, urls: list[str], out_dir: str) -> str:
    result_text = ""
    if _HAS_TQDM:
        urls = tqdm(urls)
    for original_url in urls:
        url_parse = urlparse(original_url)
        file_id = url_parse.path.removeprefix("/")
        file_name = url_parse.fragment
        go_url = f"https://fuckingfast.co/f/{file_id}/go"

        expression = f"""
        fetch("{go_url}", {{
            method: "POST",
            headers: {{
                "HX-Request": "true",
                "HX-Current-URL": "{original_url}",
                "Origin": "https://fuckingfast.co",
                "Content-Type": "application/x-www-form-urlencoded"
            }},
            body: ""
        }})
        .then(response => {{
            return {{
                status: response.status,
                headers: Object.fromEntries(response.headers.entries())
            }};
        }})
        """

        result = await tab.evaluate(
            expression, await_promise=True, return_by_value=True
        )

        try:
            direct_uri = result["headers"]["hx-redirect"]
        except KeyError:
            logger.error(f"Skipping {original_url} due to missing direct link")
            continue

        result_text += f"""{direct_uri}
    out={out_dir}/{file_name}
    continue=true
"""
    return result_text
