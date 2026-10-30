"""AF-10: License Renewal Reminder.

Notifications based on server-verified expiration dates.
No silent auto-renewal or charges — reminder only.

Design:
  * ``LicenseInfo`` holds expiration and plan details.
  * ``check_renewal_needed`` compares server time against thresholds.
  * ``RenewalAlert`` carries the reminder message and urgency.
  * All read-only — no payment or renewal actions triggered here.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional


class LicensePlan(str, Enum):
    TRIAL_24H = "trial_24h"
    TRIAL_72H = "trial_72h"
    TRIAL_CUSTOM = "trial_custom"
    STANDARD = "standard"     # 30 days / 720 hours


class AlertLevel(str, Enum):
    INFO = "info"           # > 7 days left
    NOTICE = "notice"       # 3–7 days left
    WARNING = "warning"     # 1–3 days left
    URGENT = "urgent"       # < 24 hours left
    EXPIRED = "expired"     # past expiration


@dataclass(frozen=True)
class LicenseInfo:
    """Server-verified license state."""
    plan: LicensePlan
    activated_at: float           # UTC epoch
    expires_at: float             # UTC epoch — server-authoritative
    device_id: str = ""
    license_key: str = ""

    @property
    def duration_hours(self) -> float:
        return (self.expires_at - self.activated_at) / 3600.0

    @property
    def is_trial(self) -> bool:
        return self.plan in (LicensePlan.TRIAL_24H,
                             LicensePlan.TRIAL_72H,
                             LicensePlan.TRIAL_CUSTOM)


@dataclass(frozen=True)
class RenewalAlert:
    """A renewal reminder."""
    level: AlertLevel
    hours_remaining: float
    message: str


# ── thresholds (in hours) ──────────────────────────────────────────

STANDARD_THRESHOLDS = {
    AlertLevel.NOTICE: 168.0,    # 7 days
    AlertLevel.WARNING: 72.0,    # 3 days
    AlertLevel.URGENT: 24.0,     # 1 day
}

TRIAL_THRESHOLDS = {
    AlertLevel.NOTICE: 12.0,
    AlertLevel.WARNING: 6.0,
    AlertLevel.URGENT: 1.0,
}


def check_renewal_needed(license_info: LicenseInfo,
                         server_time: float | None = None
                         ) -> Optional[RenewalAlert]:
    """Check if a renewal reminder should be shown.

    Uses server_time if provided; falls back to local clock
    (less reliable — the brief mandates server-authoritative time).

    Returns None if no reminder is needed (plenty of time left).
    """
    now = server_time if server_time is not None else time.time()
    remaining_s = license_info.expires_at - now
    remaining_h = remaining_s / 3600.0

    if remaining_h <= 0:
        return RenewalAlert(
            AlertLevel.EXPIRED, remaining_h,
            _expired_message(license_info))

    thresholds = (TRIAL_THRESHOLDS if license_info.is_trial
                  else STANDARD_THRESHOLDS)

    # Check from most urgent to least
    for level in (AlertLevel.URGENT, AlertLevel.WARNING, AlertLevel.NOTICE):
        if remaining_h <= thresholds[level]:
            return RenewalAlert(level, remaining_h,
                                _reminder_message(license_info,
                                                  remaining_h, level))

    return None  # plenty of time


def _reminder_message(info: LicenseInfo, hours: float,
                      level: AlertLevel) -> str:
    plan_label = "trial" if info.is_trial else "license"
    if hours < 1:
        time_str = f"{int(hours * 60)} minutes"
    elif hours < 48:
        time_str = f"{hours:.0f} hours"
    else:
        time_str = f"{hours / 24:.0f} days"
    return f"Your {plan_label} expires in {time_str}. Please renew to continue."


def _expired_message(info: LicenseInfo) -> str:
    plan_label = "trial" if info.is_trial else "license"
    return f"Your {plan_label} has expired. Please renew to continue using the browser."


# ── persistence ────────────────────────────────────────────────────

LICENSE_FILE = "license_state.json"


def save_license_info(app_dir: Path, info: LicenseInfo) -> None:
    """Persist license info to disk."""
    data = {
        "plan": info.plan.value,
        "activated_at": info.activated_at,
        "expires_at": info.expires_at,
        "device_id": info.device_id,
        "license_key": info.license_key,
    }
    path = app_dir / LICENSE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def load_license_info(app_dir: Path) -> Optional[LicenseInfo]:
    """Load saved license info."""
    path = app_dir / LICENSE_FILE
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return LicenseInfo(
            plan=LicensePlan(data["plan"]),
            activated_at=data["activated_at"],
            expires_at=data["expires_at"],
            device_id=data.get("device_id", ""),
            license_key=data.get("license_key", ""),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
