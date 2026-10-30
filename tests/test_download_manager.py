"""Tests for AF-05: Download Manager."""
import json
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.download_manager import (
    DownloadStatus, DownloadTracker, is_risky_download, sanitize_filename,
)


class DownloadManagerTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile_dir = Path(self.tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_start_download(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://example.com/file.zip", "file.zip", "/tmp/file.zip")
        self.assertEqual(rec.status, DownloadStatus.IN_PROGRESS)
        self.assertEqual(rec.filename, "file.zip")
        self.assertIn(rec.download_id, [r.download_id for r in t.list_all()])

    def test_complete_download(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://a.com/b", "b", "/tmp/b")
        t.complete(rec.download_id)
        self.assertEqual(t.get(rec.download_id).status, DownloadStatus.COMPLETED)

    def test_fail_download(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://a.com/b", "b", "/tmp/b")
        t.fail(rec.download_id, "network error")
        r = t.get(rec.download_id)
        self.assertEqual(r.status, DownloadStatus.FAILED)
        self.assertEqual(r.error, "network error")

    def test_cancel_download(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://a.com/b", "b", "/tmp/b")
        t.cancel(rec.download_id)
        self.assertEqual(t.get(rec.download_id).status, DownloadStatus.CANCELLED)

    def test_pause_resume(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://a.com/b", "b", "/tmp/b")
        t.pause(rec.download_id)
        self.assertEqual(t.get(rec.download_id).status, DownloadStatus.PAUSED)
        t.resume(rec.download_id)
        self.assertEqual(t.get(rec.download_id).status, DownloadStatus.IN_PROGRESS)

    def test_progress_update(self):
        t = DownloadTracker(self.profile_dir)
        rec = t.start_download("https://a.com/b", "b", "/tmp/b")
        t.update_progress(rec.download_id, 500, 1000)
        r = t.get(rec.download_id)
        self.assertEqual(r.bytes_received, 500)
        self.assertEqual(r.total_bytes, 1000)

    def test_active_downloads(self):
        t = DownloadTracker(self.profile_dir)
        r1 = t.start_download("https://a.com/1", "1", "/tmp/1")
        r2 = t.start_download("https://a.com/2", "2", "/tmp/2")
        t.complete(r1.download_id)
        active = t.active_downloads()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].download_id, r2.download_id)

    def test_clear_history(self):
        t = DownloadTracker(self.profile_dir)
        r1 = t.start_download("https://a.com/1", "1", "/tmp/1")
        r2 = t.start_download("https://a.com/2", "2", "/tmp/2")
        t.complete(r1.download_id)
        t.clear_history()
        self.assertEqual(len(t.list_all()), 1)  # only active r2 remains

    def test_persistence(self):
        t1 = DownloadTracker(self.profile_dir)
        rec = t1.start_download("https://a.com/f", "f", "/tmp/f")
        t1.complete(rec.download_id)
        # New tracker loads from disk
        t2 = DownloadTracker(self.profile_dir)
        self.assertEqual(len(t2.list_all()), 1)
        self.assertEqual(t2.list_all()[0].status, DownloadStatus.COMPLETED)

    def test_corrupt_history(self):
        (self.profile_dir / "download_history.json").write_text("BAD")
        t = DownloadTracker(self.profile_dir)
        self.assertEqual(len(t.list_all()), 0)  # graceful recovery

    def test_is_risky_download(self):
        self.assertTrue(is_risky_download("setup.exe"))
        self.assertTrue(is_risky_download("script.PS1"))
        self.assertFalse(is_risky_download("document.pdf"))
        self.assertFalse(is_risky_download("image.png"))

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("../../etc/passwd"), "download_.._.._etc_passwd")
        self.assertEqual(sanitize_filename(""), "download")
        self.assertEqual(sanitize_filename(".hidden"), "download_.hidden")
        self.assertEqual(sanitize_filename("normal.txt"), "normal.txt")


if __name__ == "__main__":
    unittest.main()
