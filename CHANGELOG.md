## [0.4.5] - 2026-08-20

### 💼 Other

- Monkey-patch `XMLHttpRequest` to capture /go requests

### ⚙️ Miscellaneous Tasks

- Bump version to 0.4.4
## [0.4.4] - 2026-08-20

### 🐛 Bug Fixes

- Stuck at some edge cases

### 🚜 Refactor

- Standalone module for the GUI part

### 📚 Documentation

- Add changelog.md
- Update changelog.md
- *(changelog)* Minor update

### ⚙️ Miscellaneous Tasks

- Re-format import orders
## [0.4.3] - 2026-08-16

### 💼 Other

- Migrate to upstream now
- Keep clean when repopulating cookies
## [0.4.2] - 2026-08-16

### 🚀 Features

- Support Microsoft Edge

### 🐛 Bug Fixes

- Do not add hard-coded mirror
- Handle browser closed by user after scraped

### 💼 Other

- Fix python3.dll must be in the directory
- Support python 3.11+

### 📚 Documentation

- *(readme)* Fix uv commands with the extra group

### ⚡ Performance

- Enhance performance on HDDs

### ⚙️ Miscellaneous Tasks

- *(windows)* Deploy packaged self-extraction LZMA2 PE
- Fix packaged path
- Release on new tag
## [0.4.0] - 2026-08-12

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

### 🐛 Bug Fixes

- Zendriver arguments
- Fitgirl does not require ff cookies
- Ignore filenotfound error
- Handle missing fuckingfast links

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

### ⚙️ Miscellaneous Tasks

- Initial PoC of `dlpass` automation
- The `BROWSER_INSTANCE` was unused
