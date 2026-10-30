"""AF-18: Accessibility Settings.

Keyboard navigation, high contrast, scaling, reduced motion,
and screen-reader usability settings.

Design:
  * ``AccessibilityConfig`` holds all a11y preferences.
  * Per-profile persistence as JSON.
  * Settings are hints to the rendering engine — actual
    enforcement depends on WebEngine support.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AccessibilityConfig:
    """Accessibility preferences for a profile."""
    # Visual
    high_contrast: bool = False
    font_scale: float = 1.0          # 0.5–3.0
    force_dark_mode: bool = False
    reduce_motion: bool = False
    reduce_transparency: bool = False

    # Navigation
    keyboard_navigation: bool = True
    focus_highlight: bool = True
    tab_cycling: bool = True

    # Content
    image_descriptions: bool = False  # request alt text
    captions: bool = False           # prefer captions for media

    # Screen reader
    screen_reader_mode: bool = False
    aria_live_announcements: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AccessibilityConfig":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})

    def validate(self) -> list[str]:
        """Validate settings and return any issues."""
        issues = []
        if self.font_scale < 0.5 or self.font_scale > 3.0:
            issues.append(f"Font scale {self.font_scale} out of range (0.5–3.0)")
        return issues


A11Y_CONFIG_FILE = "accessibility.json"


def save_config(profile_dir: Path, config: AccessibilityConfig) -> None:
    """Save accessibility config for a profile."""
    path = profile_dir / "storage" / A11Y_CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2))


def load_config(profile_dir: Path) -> AccessibilityConfig:
    """Load accessibility config; returns defaults if not found."""
    path = profile_dir / "storage" / A11Y_CONFIG_FILE
    if not path.exists():
        return AccessibilityConfig()
    try:
        data = json.loads(path.read_text())
        return AccessibilityConfig.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return AccessibilityConfig()


def get_preset(name: str) -> Optional[AccessibilityConfig]:
    """Get a named accessibility preset."""
    presets = {
        "high_visibility": AccessibilityConfig(
            high_contrast=True, font_scale=1.5,
            focus_highlight=True, reduce_motion=True),
        "screen_reader": AccessibilityConfig(
            screen_reader_mode=True, aria_live_announcements=True,
            keyboard_navigation=True, image_descriptions=True),
        "reduced_motion": AccessibilityConfig(
            reduce_motion=True, reduce_transparency=True),
        "large_text": AccessibilityConfig(font_scale=2.0),
    }
    return presets.get(name)


def list_presets() -> list[str]:
    """List available preset names."""
    return ["high_visibility", "screen_reader", "reduced_motion", "large_text"]
