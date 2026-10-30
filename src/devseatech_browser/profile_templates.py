"""AF-11: Profile Templates.

Admin-approved settings templates with no accidental sharing of
cookies or passwords.

Design:
  * ``TemplateConfig`` holds safe-to-share settings (homepage,
    search engine, proxy, extensions list — never cookies/passwords).
  * ``save_template`` / ``load_template`` persist templates as JSON.
  * ``apply_template`` copies settings into a profile dir.
  * ``list_templates`` enumerates available templates.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


# Fields that are NEVER included in a template (security boundary)
BLOCKED_FIELDS = frozenset({
    "cookies", "passwords", "vault", "session_cookies",
    "auth_tokens", "saved_logins", "credential_store",
})


@dataclass
class TemplateConfig:
    """Safe-to-share profile settings template."""
    name: str
    description: str = ""
    homepage: str = ""
    search_engine: str = ""
    proxy_url: str = ""
    user_agent: str = ""
    zoom_level: float = 1.0
    javascript_enabled: bool = True
    extensions: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0
    created_by: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        # Strip any blocked fields that might sneak into custom_settings
        if "custom_settings" in d:
            d["custom_settings"] = {
                k: v for k, v in d["custom_settings"].items()
                if k.lower() not in BLOCKED_FIELDS
            }
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "TemplateConfig":
        # Strip blocked fields
        custom = data.get("custom_settings", {})
        safe_custom = {k: v for k, v in custom.items()
                       if k.lower() not in BLOCKED_FIELDS}
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            homepage=data.get("homepage", ""),
            search_engine=data.get("search_engine", ""),
            proxy_url=data.get("proxy_url", ""),
            user_agent=data.get("user_agent", ""),
            zoom_level=data.get("zoom_level", 1.0),
            javascript_enabled=data.get("javascript_enabled", True),
            extensions=data.get("extensions", []),
            custom_settings=safe_custom,
            created_at=data.get("created_at", 0.0),
            created_by=data.get("created_by", ""),
        )


TEMPLATES_DIR = "templates"


def save_template(app_dir: Path, config: TemplateConfig) -> Path:
    """Save a template to the templates directory."""
    if not config.name:
        raise ValueError("Template name is required")
    if config.created_at == 0.0:
        config.created_at = time.time()

    templates_dir = app_dir / TEMPLATES_DIR
    templates_dir.mkdir(parents=True, exist_ok=True)

    slug = _slugify(config.name)
    path = templates_dir / f"{slug}.json"
    data = config.to_dict()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path


def load_template(app_dir: Path, name: str) -> Optional[TemplateConfig]:
    """Load a template by name."""
    slug = _slugify(name)
    path = app_dir / TEMPLATES_DIR / f"{slug}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return TemplateConfig.from_dict(data)
    except (json.JSONDecodeError, KeyError):
        return None


def list_templates(app_dir: Path) -> List[str]:
    """List available template names."""
    templates_dir = app_dir / TEMPLATES_DIR
    if not templates_dir.is_dir():
        return []
    return sorted(
        p.stem for p in templates_dir.glob("*.json")
        if not p.name.startswith(".")
    )


def delete_template(app_dir: Path, name: str) -> bool:
    """Delete a template by name. Returns True if deleted."""
    slug = _slugify(name)
    path = app_dir / TEMPLATES_DIR / f"{slug}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def apply_template(config: TemplateConfig, profile_dir: Path) -> Path:
    """Apply a template's settings to a profile directory.

    Writes a settings.json into the profile. Does NOT touch
    cookies, passwords, vault or any sensitive data.
    Returns the settings file path.
    """
    profile_dir.mkdir(parents=True, exist_ok=True)
    settings = {
        "homepage": config.homepage,
        "search_engine": config.search_engine,
        "proxy_url": config.proxy_url,
        "user_agent": config.user_agent,
        "zoom_level": config.zoom_level,
        "javascript_enabled": config.javascript_enabled,
        "extensions": config.extensions,
        "applied_template": config.name,
        "applied_at": time.time(),
    }
    settings.update(config.custom_settings)
    path = profile_dir / "settings.json"
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False))
    return path


def _slugify(name: str) -> str:
    """Convert a template name to a filesystem-safe slug."""
    slug = name.lower().strip()
    safe = []
    for ch in slug:
        if ch.isalnum() or ch in "-_":
            safe.append(ch)
        elif ch in " .":
            safe.append("-")
    return "".join(safe) or "template"
