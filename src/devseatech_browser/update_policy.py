"""Pure decision logic for DevSeaTech Browser release eligibility.

This does not fetch, download, install, or verify packages. The real update
service must independently verify signatures and enforce authorization.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdatePolicy:
    auto_update_enabled: bool = False


@dataclass(frozen=True)
class ReleaseCandidate:
    published: bool
    approved: bool
    signature_verified: bool
    compatible: bool
    downgrade: bool = False


def eligible_for_automatic_install(
    policy: UpdatePolicy, release: ReleaseCandidate
) -> bool:
    """Fail closed: a Git push alone cannot trigger an automatic update."""
    return (
        policy.auto_update_enabled
        and release.published
        and release.approved
        and release.signature_verified
        and release.compatible
        and not release.downgrade
    )
