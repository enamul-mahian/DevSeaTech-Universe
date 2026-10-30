"""Pure profile discovery for GUI and headless tests."""
from pathlib import Path


def list_profiles(root: Path) -> list[str]:
    """List valid on-disk profiles without following symbolic links or writing."""
    if not root.is_dir():
        return []
    return sorted(
        entry.name for entry in root.iterdir()
        if entry.is_dir() and not entry.is_symlink()
        and 0 < len(entry.name) <= 40
        and all(ch.isalnum() or ch in "-_" for ch in entry.name)
    )
