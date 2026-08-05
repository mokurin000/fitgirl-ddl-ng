# fitgirl-ddl-ng

Next generation of `fitgirl-ddl`, solving cloudflare turnstile.

## Scrape urls

For example,

```bash
uv run scrape-fitgirl https://fitgirl-repacks.site/waterpark-simulator/
```

you would have `waterpark-simulator.txt`.

## Refresh cookies

Refresh `FuckingFast.co` cookies, so you could perform DDL extraction in 25 minutes

```bash
uv run refresh-cookies
```

## DDL Extraction

```bash
uv run extract-ddl waterpark-simulator.txt
```

## Build

To build CLI exe's with `pyinstaler`:

```bash
uv pip install pyinstaller
uv run pyinstaller --no-confirm fitgirl-cli.spec
```
