## [0.4.3] - 2026-08-16

### 💼 Other

- Migrate to upstream now
- Keep clean when repopulating cookies
## [0.4.2] - 2026-08-16

### 🚀 Features

- Export dlpass & cf_clearance cookies
- Scrape fuckingfast urls
- Extract & scrape cli tool using typer
- Grouped download
- Implement progress bar during extraction
- Support force refresh cookies
- Support extract multiple files in single instance
- Implement basic simple GUI
- Enable auto dark mode support
- Support Microsoft Edge

### 🐛 Bug Fixes

- Zendriver arguments
- Fitgirl does not require ff cookies
- Ignore filenotfound error
- Handle missing fuckingfast links
- Do not add hard-coded mirror
- Handle browser closed by user after scraped

### 💼 Other

- Migrate to zendriver
- No more async task needed
- Enhance logging via loguru
- Skip `File was deleted` e.g.
- Implement ddl extract cli
- Re-design scrape to support scraping multiple games
- Bundle using pyintaller
- Opencv no longer used
- Set behavior to `deny`, avoid download dir issue
- Failure logging
- Support deploying to windows x64
- Logging that browser is stopping
- Fix missing metainfo for prompt_toolkit
- Don't wait for interactive, sometimes get stuck
- Package GUI installer
- Avoid file confliction when merge aria2 inputs
- Start `headless` chrome when possible
- Optional deps group for CLI
- Split scripts for CLI build
- Fix missing positional argument
- Grab window focus after started Chrome
- Window-less launcher for the GUI window
- Deploy GUI version
- Repackage support
- Package GUI using `._pth`
- Centre window, save to aria2/
- Per-game & per-file progress bars
- Remove the previously packged exe
- Fix python3.dll must be in the directory
- Support python 3.11+

### 🚜 Refactor

- Split up modules
- Split functions for scraping and cookies population
- Worker, group_dialog, main_frame

### 📚 Documentation

- *(readme)* Document on usage
- *(readme)* Pre-built exe using pyinstaller
- *(readme)* Prerequisites
- *(readme)* Package using python-embed
- *(readme)* Bundle commands
- *(readme)* Fix uv commands with the extra group

### ⚡ Performance

- Enhance performance on HDDs

### ⚙️ Miscellaneous Tasks

- Initial PoC of `dlpass` automation
- The `BROWSER_INSTANCE` was unused
- *(windows)* Deploy packaged self-extraction LZMA2 PE
- Fix packaged path
- Release on new tag
