"""Reject malicious backup manifest paths without changing the filesystem."""
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from devseatech_browser.backup import restore_backup


def forged_bundle(path):
    manifest = {"files": [{"path": path, "sha256": "0" * 64, "size": 0}]}
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w"):
        pass
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:
        for name, data in (
            ("manifest.json", json.dumps(manifest).encode()),
            ("payload.tar", payload.getvalue()),
        ):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return raw.getvalue()


class RestorePathValidationTests(unittest.TestCase):
    def test_malicious_paths_rejected_without_writes(self):
        for malicious in ("../outside.txt", "/absolute", "dir/../escape",
                          "dir//file", "C:/Windows/file", "dir\\evil", "", "./file"):
            with self.subTest(path=malicious), tempfile.TemporaryDirectory() as temp:
                target = Path(temp) / "restored"
                placeholder = Path(temp) / "dummy.dstbak"
                placeholder.write_bytes(b"placeholder")
                with patch("devseatech_browser.backup._decrypt",
                           return_value=forged_bundle(malicious)):
                    with self.assertRaises(ValueError):
                        restore_backup(placeholder, "passphrase", target)
                self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
