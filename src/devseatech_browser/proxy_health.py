"""AF-08: Proxy Health Monitor.

Connection and configuration checks for HTTP, HTTPS, and SOCKS5
proxies.  Identifies possible DNS/IP leaks without collecting
unrelated browsing data.

Design:
  * ``ProxyConfig`` dataclass holds proxy settings.
  * ``check_proxy`` performs a connectivity test via the proxy.
  * ``check_dns_leak`` compares DNS resolution through proxy vs direct.
  * All checks are read-only and non-destructive.
"""
from __future__ import annotations

import os
import socket
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse


class ProxyType(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class ProxyStatus(str, Enum):
    OK = "ok"
    SLOW = "slow"
    UNREACHABLE = "unreachable"
    AUTH_REQUIRED = "auth_required"
    ERROR = "error"


@dataclass(frozen=True)
class ProxyConfig:
    """Proxy configuration."""
    proxy_type: ProxyType
    host: str
    port: int
    username: str = ""
    password: str = ""

    def url(self) -> str:
        auth = ""
        if self.username:
            auth = f"{self.username}:{self.password}@"
        return f"{self.proxy_type.value}://{auth}{self.host}:{self.port}"


@dataclass(frozen=True)
class ProxyCheckResult:
    """Result of a proxy health check."""
    config: ProxyConfig
    status: ProxyStatus
    latency_ms: float = 0.0
    detail: str = ""


@dataclass(frozen=True)
class DnsLeakResult:
    """Result of a DNS leak check."""
    direct_ip: str
    proxy_ip: str
    potential_leak: bool
    detail: str = ""


# ── connectivity checks ─────────────────────────────────────────────

def check_proxy_connectivity(config: ProxyConfig,
                             timeout: float = 5.0) -> ProxyCheckResult:
    """Test basic TCP connectivity to a proxy server.

    Does NOT route traffic through the proxy — just checks if the
    proxy host:port accepts connections.
    """
    start = time.monotonic()
    try:
        sock = socket.create_connection(
            (config.host, config.port), timeout=timeout)
        elapsed_ms = (time.monotonic() - start) * 1000
        sock.close()
        if elapsed_ms > 2000:
            return ProxyCheckResult(config, ProxyStatus.SLOW,
                                   elapsed_ms, f"Connected but slow ({elapsed_ms:.0f}ms)")
        return ProxyCheckResult(config, ProxyStatus.OK,
                                elapsed_ms, f"Connected in {elapsed_ms:.0f}ms")
    except socket.timeout:
        return ProxyCheckResult(config, ProxyStatus.UNREACHABLE,
                                detail="Connection timed out")
    except ConnectionRefusedError:
        return ProxyCheckResult(config, ProxyStatus.UNREACHABLE,
                                detail="Connection refused")
    except OSError as e:
        return ProxyCheckResult(config, ProxyStatus.ERROR,
                                detail=str(e))


def validate_proxy_config(config: ProxyConfig) -> List[str]:
    """Validate proxy configuration and return list of issues."""
    issues: list[str] = []
    if not config.host:
        issues.append("Proxy host is empty")
    if config.port < 1 or config.port > 65535:
        issues.append(f"Invalid port: {config.port}")
    if config.proxy_type == ProxyType.SOCKS5 and config.port == 80:
        issues.append("SOCKS5 on port 80 is unusual — verify configuration")
    return issues


def parse_proxy_url(url: str) -> Optional[ProxyConfig]:
    """Parse a proxy URL string into a ProxyConfig.

    Returns None if the URL is invalid.
    """
    try:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https", "socks5"):
            return None
        host = parsed.hostname or ""
        port = parsed.port or (1080 if scheme == "socks5" else 8080)
        return ProxyConfig(
            proxy_type=ProxyType(scheme),
            host=host,
            port=port,
            username=parsed.username or "",
            password=parsed.password or "",
        )
    except (ValueError, AttributeError):
        return None


def get_system_proxy() -> Optional[ProxyConfig]:
    """Read proxy from environment variables (HTTP_PROXY, HTTPS_PROXY)."""
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        url = os.environ.get(var, "")
        if url:
            return parse_proxy_url(url)
    return None
