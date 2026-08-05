from urllib.parse import urlparse

from zendriver import Tab


async def extract_ddl(tab: Tab, urls: list[str]) -> str:
    result_text = ""
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
        direct_uri = result["headers"]["hx-redirect"]
        result_text += f"""{direct_uri}
    out={file_name}
    continue=true
"""
    return result_text
