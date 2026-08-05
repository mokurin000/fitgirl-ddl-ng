import os
import time
import tempfile
from pathlib import Path

TEMP_DIR = str(Path(tempfile.gettempdir()) / "fitgirl-ddl-ng")
COOKIES_SESSION = Path(__file__).parent / "cookies.dat"


def cookies_valid() -> bool:
    try:
        mtime = os.path.getmtime(COOKIES_SESSION)
        if time.time() - mtime < 1800:
            return True
    except FileNotFoundError:
        pass

    return False
