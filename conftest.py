"""Root conftest: ensure src/ is on sys.path for all tests."""
import sys
from pathlib import Path

src = str(Path(__file__).parent / "src")
if src not in sys.path:
    sys.path.insert(0, src)
