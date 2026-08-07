# fitgirl-ddl-ng

Next generation of `fitgirl-ddl`, working with latest `fuckingfast.co`.

## Prerequisites

- `Chrome`, `Chromium`, or `Brave` browser installed.
- Network connection that could pass the cloudflare turnstile.

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
