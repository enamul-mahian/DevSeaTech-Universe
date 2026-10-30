"""AF-09: Resource Manager.

Per-profile CPU, RAM and disk monitoring with low-overhead measurement
and actionable limits.

Design:
  * ``ResourceSnapshot`` captures a point-in-time measurement.
  * ``measure_process`` collects CPU/RSS from the current process.
  * ``measure_profile_disk`` scans a profile directory for size.
  * ``ResourcePolicy`` defines thresholds and ``check_policy``
    returns which limits are breached.
  * All operations are read-only and non-destructive.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class ResourceKind(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ResourceSnapshot:
    """Point-in-time resource measurement."""
    kind: ResourceKind
    value: float        # percent for CPU/RAM, bytes for disk
    label: str = ""
    timestamp: float = 0.0


@dataclass(frozen=True)
class PolicyViolation:
    """A threshold that has been breached."""
    kind: ResourceKind
    severity: Severity
    current: float
    threshold: float
    message: str


@dataclass
class ResourcePolicy:
    """Configurable resource thresholds."""
    cpu_warning_pct: float = 80.0
    cpu_critical_pct: float = 95.0
    memory_warning_bytes: int = 512 * 1024 * 1024      # 512 MiB
    memory_critical_bytes: int = 1024 * 1024 * 1024     # 1 GiB
    disk_warning_bytes: int = 1024 * 1024 * 1024        # 1 GiB
    disk_critical_bytes: int = 2 * 1024 * 1024 * 1024   # 2 GiB


# ── measurement helpers ────────────────────────────────────────────

def _read_proc_stat() -> Optional[dict]:
    """Read /proc/self/stat for CPU ticks (Linux only)."""
    try:
        with open("/proc/self/stat") as f:
            parts = f.read().split()
        # utime=13, stime=14 (0-indexed)
        utime = int(parts[13])
        stime = int(parts[14])
        return {"utime": utime, "stime": stime,
                "total": utime + stime,
                "clock": time.monotonic()}
    except (OSError, IndexError, ValueError):
        return None


def _read_proc_status_rss() -> Optional[int]:
    """Read VmRSS from /proc/self/status (Linux only), in bytes."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024  # kB → bytes
    except (OSError, ValueError):
        pass
    return None


def measure_memory() -> ResourceSnapshot:
    """Measure current process RSS."""
    rss = _read_proc_status_rss()
    if rss is not None:
        return ResourceSnapshot(ResourceKind.MEMORY, float(rss),
                                f"RSS: {rss / (1024*1024):.1f} MiB",
                                time.time())
    # Fallback: resource module
    try:
        import resource as res
        usage = res.getrusage(res.RUSAGE_SELF)
        # maxrss is in KB on Linux
        rss_bytes = usage.ru_maxrss * 1024
        return ResourceSnapshot(ResourceKind.MEMORY, float(rss_bytes),
                                f"Peak RSS: {rss_bytes / (1024*1024):.1f} MiB",
                                time.time())
    except (ImportError, AttributeError):
        return ResourceSnapshot(ResourceKind.MEMORY, 0.0,
                                "Memory measurement unavailable",
                                time.time())


def measure_profile_disk(profile_dir: Path) -> ResourceSnapshot:
    """Measure total disk usage of a profile directory."""
    if not profile_dir.is_dir():
        return ResourceSnapshot(ResourceKind.DISK, 0.0,
                                f"Not found: {profile_dir}",
                                time.time())
    total = 0
    for dirpath, _dirnames, filenames in os.walk(profile_dir):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                if not os.path.islink(fp):
                    total += os.path.getsize(fp)
            except OSError:
                pass
    return ResourceSnapshot(ResourceKind.DISK, float(total),
                            f"{total / (1024*1024):.1f} MiB",
                            time.time())


def measure_all_profiles_disk(profiles_dir: Path) -> List[ResourceSnapshot]:
    """Measure disk usage per profile."""
    if not profiles_dir.is_dir():
        return []
    results = []
    for child in sorted(profiles_dir.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            snap = measure_profile_disk(child)
            results.append(ResourceSnapshot(
                snap.kind, snap.value,
                f"{child.name}: {snap.label}",
                snap.timestamp))
    return results


# ── policy checks ──────────────────────────────────────────────────

def check_policy(snapshots: List[ResourceSnapshot],
                 policy: ResourcePolicy | None = None
                 ) -> List[PolicyViolation]:
    """Check resource snapshots against policy thresholds."""
    if policy is None:
        policy = ResourcePolicy()
    violations: list[PolicyViolation] = []

    for snap in snapshots:
        if snap.kind == ResourceKind.MEMORY:
            if snap.value >= policy.memory_critical_bytes:
                violations.append(PolicyViolation(
                    ResourceKind.MEMORY, Severity.CRITICAL,
                    snap.value, float(policy.memory_critical_bytes),
                    f"Memory critical: {snap.value/(1024*1024):.0f} MiB "
                    f"≥ {policy.memory_critical_bytes/(1024*1024):.0f} MiB"))
            elif snap.value >= policy.memory_warning_bytes:
                violations.append(PolicyViolation(
                    ResourceKind.MEMORY, Severity.WARNING,
                    snap.value, float(policy.memory_warning_bytes),
                    f"Memory warning: {snap.value/(1024*1024):.0f} MiB "
                    f"≥ {policy.memory_warning_bytes/(1024*1024):.0f} MiB"))

        elif snap.kind == ResourceKind.DISK:
            if snap.value >= policy.disk_critical_bytes:
                violations.append(PolicyViolation(
                    ResourceKind.DISK, Severity.CRITICAL,
                    snap.value, float(policy.disk_critical_bytes),
                    f"Disk critical: {snap.value/(1024*1024):.0f} MiB "
                    f"≥ {policy.disk_critical_bytes/(1024*1024):.0f} MiB"))
            elif snap.value >= policy.disk_warning_bytes:
                violations.append(PolicyViolation(
                    ResourceKind.DISK, Severity.WARNING,
                    snap.value, float(policy.disk_warning_bytes),
                    f"Disk warning: {snap.value/(1024*1024):.0f} MiB "
                    f"≥ {policy.disk_warning_bytes/(1024*1024):.0f} MiB"))

        elif snap.kind == ResourceKind.CPU:
            if snap.value >= policy.cpu_critical_pct:
                violations.append(PolicyViolation(
                    ResourceKind.CPU, Severity.CRITICAL,
                    snap.value, policy.cpu_critical_pct,
                    f"CPU critical: {snap.value:.1f}% ≥ {policy.cpu_critical_pct}%"))
            elif snap.value >= policy.cpu_warning_pct:
                violations.append(PolicyViolation(
                    ResourceKind.CPU, Severity.WARNING,
                    snap.value, policy.cpu_warning_pct,
                    f"CPU warning: {snap.value:.1f}% ≥ {policy.cpu_warning_pct}%"))

    return violations


def format_report(snapshots: List[ResourceSnapshot],
                  violations: List[PolicyViolation]) -> str:
    """Format a human-readable resource report."""
    lines = ["=== Resource Report ==="]
    for snap in snapshots:
        lines.append(f"  [{snap.kind.value.upper()}] {snap.label}")
    if violations:
        lines.append("")
        lines.append("Violations:")
        for v in violations:
            lines.append(f"  [{v.severity.value.upper()}] {v.message}")
    else:
        lines.append("\nAll resources within limits.")
    return "\n".join(lines)
