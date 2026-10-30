"""AF-17: Website Translation.

Explicit website translation without changing English product UI.
Privacy disclosure for network translation services.

Design:
  * ``TranslationConfig`` holds user preferences.
  * ``TranslationRequest`` describes what to translate.
  * Privacy: always disclose when content will be sent to a
    network translation service.
  * Product UI remains English — only website content is translated.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional


class TranslationProvider(str):
    """Translation service identifier."""
    pass


BUILTIN_PROVIDER = TranslationProvider("builtin")


@dataclass
class TranslationConfig:
    """User translation preferences."""
    enabled: bool = False
    target_language: str = ""        # ISO 639-1 code e.g. "bn", "es"
    auto_translate: bool = False     # auto-translate all pages
    excluded_sites: List[str] = field(default_factory=list)
    provider: str = "builtin"
    privacy_acknowledged: bool = False  # user saw privacy disclosure

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TranslationConfig":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


@dataclass(frozen=True)
class TranslationRequest:
    """A request to translate content."""
    source_lang: str       # detected or specified
    target_lang: str
    text: str
    origin: str = ""       # website origin


@dataclass(frozen=True)
class PrivacyDisclosure:
    """Privacy notice shown before first network translation."""
    provider: str
    message: str
    data_sent: List[str]   # what data will be transmitted


PRIVACY_DISCLOSURE = PrivacyDisclosure(
    provider="builtin",
    message=(
        "Website content will be sent to a translation service for "
        "processing. This may include the text content of the page "
        "you are viewing. The browser UI will remain in English."
    ),
    data_sent=["page_text_content", "source_language", "target_language"],
)


TRANSLATION_CONFIG_FILE = "translation_config.json"


def save_config(profile_dir: Path, config: TranslationConfig) -> None:
    """Save translation config for a profile."""
    path = profile_dir / "storage" / TRANSLATION_CONFIG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2))


def load_config(profile_dir: Path) -> TranslationConfig:
    """Load translation config; returns defaults if not found."""
    path = profile_dir / "storage" / TRANSLATION_CONFIG_FILE
    if not path.exists():
        return TranslationConfig()
    try:
        data = json.loads(path.read_text())
        return TranslationConfig.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return TranslationConfig()


def is_site_excluded(config: TranslationConfig, origin: str) -> bool:
    """Check if a site is excluded from auto-translation."""
    return any(exc in origin for exc in config.excluded_sites)


def needs_privacy_disclosure(config: TranslationConfig) -> bool:
    """Check if privacy disclosure needs to be shown."""
    return config.enabled and not config.privacy_acknowledged


def get_supported_languages() -> List[Dict[str, str]]:
    """Return list of supported target languages."""
    return [
        {"code": "bn", "name": "Bengali"},
        {"code": "zh", "name": "Chinese"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "hi", "name": "Hindi"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "ar", "name": "Arabic"},
        {"code": "tr", "name": "Turkish"},
    ]
