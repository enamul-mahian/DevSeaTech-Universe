"""Tests for the browser home page generator."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from devseatech_browser.home_page import (
    SpeedDialEntry,
    DEFAULT_SPEED_DIAL,
    generate_home_html,
    load_speed_dial,
    save_speed_dial,
    get_home_page_url,
)


class TestSpeedDial(unittest.TestCase):
    """Speed dial persistence tests."""

    def test_default_entries(self):
        """Defaults include Google, YouTube, etc."""
        self.assertTrue(len(DEFAULT_SPEED_DIAL) >= 6)
        titles = [e["title"] for e in DEFAULT_SPEED_DIAL]
        self.assertIn("Google", titles)
        self.assertIn("YouTube", titles)

    def test_load_missing_file_returns_defaults(self):
        """Missing file falls back to defaults."""
        with patch("devseatech_browser.home_page.SPEED_DIAL_FILE",
                    Path("/nonexistent/speed_dial.json")):
            entries = load_speed_dial()
        self.assertEqual(len(entries), len(DEFAULT_SPEED_DIAL))
        self.assertEqual(entries[0].title, "Google")

    def test_save_and_load_roundtrip(self):
        """Saved entries load back correctly."""
        entries = [
            SpeedDialEntry("Test", "https://test.com", "T"),
            SpeedDialEntry("Example", "https://example.com", "E"),
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "speed_dial.json"
            with patch("devseatech_browser.home_page.SPEED_DIAL_FILE", path):
                save_speed_dial(entries)
                loaded = load_speed_dial()
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].title, "Test")
            self.assertEqual(loaded[1].url, "https://example.com")

    def test_corrupt_file_returns_defaults(self):
        """Corrupt JSON falls back to defaults."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "speed_dial.json"
            path.write_text("not json!", encoding="utf-8")
            with patch("devseatech_browser.home_page.SPEED_DIAL_FILE", path):
                entries = load_speed_dial()
            self.assertEqual(len(entries), len(DEFAULT_SPEED_DIAL))


class TestHomeHtml(unittest.TestCase):
    """Home page HTML generation tests."""

    def test_generates_valid_html(self):
        """Output is a complete HTML document."""
        html = generate_home_html([
            SpeedDialEntry("Test", "https://test.com", "T"),
        ])
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("</html>", html)
        self.assertIn("DevSeaTech Universe", html)

    def test_tiles_appear_in_html(self):
        """Speed dial entries appear as tiles."""
        entries = [
            SpeedDialEntry("MyFav", "https://myfav.site", "M"),
        ]
        html = generate_home_html(entries)
        self.assertIn("MyFav", html)
        self.assertIn("https://myfav.site", html)

    def test_search_form_present(self):
        """Google search form is embedded."""
        html = generate_home_html([])
        self.assertIn("google.com/search", html)
        self.assertIn('name="q"', html)

    def test_html_escaping(self):
        """Special chars in titles are escaped."""
        entries = [
            SpeedDialEntry('<script>alert(1)</script>', "https://x.com", "&"),
        ]
        html = generate_home_html(entries)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_get_home_page_url_returns_file_uri(self):
        """get_home_page_url produces a file:// URI."""
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td) / "cache"
            with patch("devseatech_browser.home_page.Path.home",
                        return_value=Path(td)):
                # We need to also patch SPEED_DIAL_FILE
                with patch("devseatech_browser.home_page.SPEED_DIAL_FILE",
                            Path(td) / "speed_dial.json"):
                    url = get_home_page_url()
        self.assertTrue(url.startswith("file://"))
        self.assertTrue(url.endswith("home.html"))

    def test_default_entries_used(self):
        """When no entries passed, defaults are used."""
        with patch("devseatech_browser.home_page.SPEED_DIAL_FILE",
                    Path("/nonexistent/file.json")):
            html = generate_home_html()
        self.assertIn("Google", html)
        self.assertIn("YouTube", html)


if __name__ == "__main__":
    unittest.main()
