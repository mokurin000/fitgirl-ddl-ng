# fitgirl-ddl-ng

Next generation of `fitgirl-ddl`, working with latest `fuckingfast.co`.

## Prerequisites

- `Chrome`, `Microsoft Edge`, `Chromium`, or `Brave` browser installed.
- Network connection that could pass the cloudflare turnstile.

## Development

```bash
uv sync --dev --all-extras
```

Or,

```bash
pip install -e .[cli,gui]
```

## Scrape urls

For example,

```bash
uv run --extra cli scrape-fitgirl https://fitgirl-repacks.site/waterpark-simulator/
```

you would have `waterpark-simulator.txt`.

## DDL Extraction

```bash
uv run --extra cli extract-ddl waterpark-simulator.txt
```
