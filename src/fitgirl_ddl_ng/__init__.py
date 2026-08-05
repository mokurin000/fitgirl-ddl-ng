import os
import time
import tempfile
from pathlib import Path

TEMP_DIR = str(Path(tempfile.gettempdir()) / "fitgirl-ddl-ng")
COOKIES_SESSION = Path(__file__).parent / "cookies.dat"


def cookies_valid() -> bool:
    os.makedirs(Path(__file__).parent, exist_ok=True)

    try:
        mtime = os.path.getmtime(COOKIES_SESSION)
        # Leave 5 minutes for scraping
        if time.time() - mtime < 1500:
            return True
    except FileNotFoundError:
        pass

    return False
