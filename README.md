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

## Build

To build CLI exe's with `pyinstaler`:

```bash
uv pip install pyinstaller
uv run pyinstaller --no-confirm fitgirl-cli.spec
```

Alternatively, for example, using python-embed to package for windows CPython 3.14.7:

```bash
# Download the latest python embed 3.14 build here
mkdir -p deploy && cd deploy

python_ver=3.14
python_dir="python-${python_ver}.7-embed-amd64"

# enable the site-packages support
sed -i 's/#import site/import site/g' ${python_dir}/python314._pth
# install dependencies
pip3.14 install . -t ${python_dir}/Lib/site-packages

# clean-up *.pyc
rm -rf ${python_dir}/Lib/site-packages/**/__pycache__
```
