"""AF-06: Secure Password Vault.

Encrypted credential storage per profile.  Credentials are encrypted
at rest using Fernet with a scrypt-derived key (same pattern as AF-02
backup encryption).  The vault never logs plaintext secrets.

Design:
  * Each profile has its own vault file (``vault.enc``) inside the
    profile's storage directory.
  * Credentials are keyed by ``(origin, username)`` — one entry per
    site+user combination.
  * Export of credentials requires explicit admin authorization
    (enforced by the caller / UI layer, not this module).
  * The vault uses the same ``_derive_key`` / Fernet pattern from
    ``backup.py`` to avoid duplicating crypto code.

This module provides the storage layer only.  UI integration and
OS-keystore backing are separate concerns.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Lazy-import cryptography so the module loads even without it.
_HAS_CRYPTO = False
try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    import base64
    _HAS_CRYPTO = True
except ImportError:
    pass


def has_crypto() -> bool:
    return _HAS_CRYPTO


@dataclass
class Credential:
    """One saved credential."""
    origin: str       # e.g. "https://github.com"
    username: str
    password: str      # plaintext in memory only; encrypted on disk
    notes: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0

    def key(self) -> Tuple[str, str]:
        return (self.origin, self.username)


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a passphrase using scrypt."""
    if not _HAS_CRYPTO:
        raise RuntimeError("cryptography package not installed")
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    raw = kdf.derive(passphrase.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def _encrypt(data: bytes, passphrase: str) -> bytes:
    """Encrypt data with a passphrase. Returns salt (16) + ciphertext."""
    salt = os.urandom(16)
    key = _derive_key(passphrase, salt)
    f = Fernet(key)
    return salt + f.encrypt(data)


def _decrypt(blob: bytes, passphrase: str) -> bytes:
    """Decrypt salt-prefixed blob."""
    if len(blob) < 17:
        raise ValueError("Encrypted data too short")
    salt, ciphertext = blob[:16], blob[16:]
    key = _derive_key(passphrase, salt)
    f = Fernet(key)
    return f.decrypt(ciphertext)


class PasswordVault:
    """Encrypted credential store for one profile."""

    def __init__(self, profile_dir: Path):
        self._profile_dir = profile_dir
        self._vault_path = profile_dir / "storage" / "vault.enc"
        self._credentials: Dict[Tuple[str, str], Credential] = {}
        self._unlocked = False

    @property
    def is_unlocked(self) -> bool:
        return self._unlocked

    def unlock(self, passphrase: str) -> bool:
        """Decrypt and load the vault. Returns True on success."""
        if not _HAS_CRYPTO:
            return False
        if not self._vault_path.exists():
            # No vault yet — create empty one on first save
            self._unlocked = True
            self._passphrase = passphrase
            return True
        try:
            blob = self._vault_path.read_bytes()
            plaintext = _decrypt(blob, passphrase)
            data = json.loads(plaintext.decode("utf-8"))
            self._credentials = {}
            for entry in data:
                c = Credential(**entry)
                self._credentials[c.key()] = c
            self._passphrase = passphrase
            self._unlocked = True
            return True
        except (InvalidToken, ValueError, OSError, KeyError, TypeError):
            return False

    def lock(self) -> None:
        """Clear in-memory credentials and lock."""
        self._credentials.clear()
        self._unlocked = False
        self._passphrase = ""

    def _save(self) -> None:
        """Encrypt and write vault to disk."""
        if not self._unlocked:
            raise RuntimeError("Vault is locked")
        entries = [asdict(c) for c in self._credentials.values()]
        plaintext = json.dumps(entries, ensure_ascii=False).encode("utf-8")
        encrypted = _encrypt(plaintext, self._passphrase)
        self._vault_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._vault_path.with_suffix(".tmp")
        with tmp.open("wb") as fh:
            fh.write(encrypted)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        tmp.replace(self._vault_path)

    def add(self, origin: str, username: str, password: str,
            notes: str = "") -> Credential:
        """Add or update a credential."""
        if not self._unlocked:
            raise RuntimeError("Vault is locked")
        now = time.time()
        key = (origin, username)
        existing = self._credentials.get(key)
        c = Credential(
            origin=origin, username=username, password=password,
            notes=notes,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )
        self._credentials[key] = c
        self._save()
        return c

    def remove(self, origin: str, username: str) -> bool:
        """Remove a credential. Returns True if it existed."""
        if not self._unlocked:
            raise RuntimeError("Vault is locked")
        key = (origin, username)
        if key in self._credentials:
            del self._credentials[key]
            self._save()
            return True
        return False

    def get(self, origin: str, username: str) -> Optional[Credential]:
        """Retrieve a credential."""
        return self._credentials.get((origin, username))

    def list_origins(self) -> List[str]:
        """List unique origins with saved credentials."""
        return sorted(set(c.origin for c in self._credentials.values()))

    def list_for_origin(self, origin: str) -> List[Credential]:
        """List credentials for a specific origin."""
        return [c for c in self._credentials.values() if c.origin == origin]

    def list_all(self) -> List[Credential]:
        """List all credentials (vault must be unlocked)."""
        return list(self._credentials.values())

    def export_all(self) -> List[dict]:
        """Export all credentials as dicts (for authorized export).

        The caller is responsible for admin authorization checks.
        """
        if not self._unlocked:
            raise RuntimeError("Vault is locked")
        return [asdict(c) for c in self._credentials.values()]

    def count(self) -> int:
        return len(self._credentials)
