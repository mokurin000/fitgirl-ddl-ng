import tempfile
from pathlib import Path

TEMP_DIR = str(Path(tempfile.gettempdir()) / "fitgirl-ddl-ng")
COOKIES_SESSION = Path(__file__).parent / "cookies.dat"
