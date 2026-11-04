"""Fail-closed subscription access decisions for the desktop launcher.

This module does not authenticate users or verify server signatures.
Only pass a status from a trusted, authenticated server response.
Do not use local clocks or cached payment redirects to grant access.
"""
from __future__ import annotations

from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    EXPIRED = "expired"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"
    UNKNOWN = "unknown"


def may_launch_browser(status: SubscriptionStatus, *, server_verified: bool) -> bool:
    """Allow launches only with an authenticated current entitlement."""
    return server_verified and status in {
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.TRIALING,
    }


def expiry_policy() -> dict[str, object]:
    """Non-destructive policy for subscription expiry and renewal."""
    return {
        "preserve_local_profiles": True,
        "preserve_cookies_cache_bookmarks": True,
        "delete_local_data_on_expiry": False,
        "block_browser_launch_until_renewal": True,
        "server_verification_required": True,
    }
