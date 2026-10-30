"""Tests for AF-06: Secure Password Vault."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.password_vault import (
    PasswordVault, has_crypto, Credential,
)

HAS_CRYPTO = has_crypto()


class PureVaultTests(unittest.TestCase):
    """Tests that work without cryptography."""

    def test_has_crypto_is_bool(self):
        self.assertIsInstance(has_crypto(), bool)

    def test_credential_key(self):
        c = Credential("https://example.com", "user", "pass")
        self.assertEqual(c.key(), ("https://example.com", "user"))


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class VaultEncryptionTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile_dir = Path(self.tmp) / "profile"
        (self.profile_dir / "storage").mkdir(parents=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_unlock_empty_vault(self):
        v = PasswordVault(self.profile_dir)
        self.assertTrue(v.unlock("master-passphrase"))
        self.assertTrue(v.is_unlocked)
        self.assertEqual(v.count(), 0)

    def test_add_and_retrieve(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass123")
        v.add("https://github.com", "alice", "s3cret", notes="work")
        c = v.get("https://github.com", "alice")
        self.assertIsNotNone(c)
        self.assertEqual(c.password, "s3cret")
        self.assertEqual(c.notes, "work")

    def test_persistence_and_decrypt(self):
        v1 = PasswordVault(self.profile_dir)
        v1.unlock("mypass")
        v1.add("https://example.com", "bob", "pw123")
        v1.lock()

        v2 = PasswordVault(self.profile_dir)
        self.assertTrue(v2.unlock("mypass"))
        self.assertEqual(v2.count(), 1)
        c = v2.get("https://example.com", "bob")
        self.assertEqual(c.password, "pw123")

    def test_wrong_passphrase(self):
        v1 = PasswordVault(self.profile_dir)
        v1.unlock("correct")
        v1.add("https://a.com", "u", "p")
        v1.lock()

        v2 = PasswordVault(self.profile_dir)
        self.assertFalse(v2.unlock("wrong"))
        self.assertFalse(v2.is_unlocked)

    def test_update_credential(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://a.com", "u", "old")
        v.add("https://a.com", "u", "new")
        self.assertEqual(v.count(), 1)
        self.assertEqual(v.get("https://a.com", "u").password, "new")

    def test_remove_credential(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://a.com", "u", "p")
        self.assertTrue(v.remove("https://a.com", "u"))
        self.assertEqual(v.count(), 0)
        self.assertFalse(v.remove("https://a.com", "u"))  # already gone

    def test_list_origins(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://b.com", "u1", "p")
        v.add("https://a.com", "u2", "p")
        v.add("https://b.com", "u3", "p")
        origins = v.list_origins()
        self.assertEqual(origins, ["https://a.com", "https://b.com"])

    def test_list_for_origin(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://a.com", "u1", "p1")
        v.add("https://a.com", "u2", "p2")
        v.add("https://b.com", "u3", "p3")
        creds = v.list_for_origin("https://a.com")
        self.assertEqual(len(creds), 2)

    def test_export_all(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://a.com", "u", "p")
        exported = v.export_all()
        self.assertEqual(len(exported), 1)
        self.assertIn("password", exported[0])

    def test_lock_clears_memory(self):
        v = PasswordVault(self.profile_dir)
        v.unlock("pass")
        v.add("https://a.com", "u", "p")
        v.lock()
        self.assertFalse(v.is_unlocked)
        self.assertEqual(v.count(), 0)

    def test_locked_vault_raises(self):
        v = PasswordVault(self.profile_dir)
        with self.assertRaises(RuntimeError):
            v.add("https://a.com", "u", "p")


if __name__ == "__main__":
    unittest.main()
