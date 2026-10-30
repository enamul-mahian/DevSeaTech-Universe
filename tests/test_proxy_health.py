"""Tests for AF-08: Proxy Health Monitor."""
import unittest

from devseatech_browser.proxy_health import (
    ProxyConfig, ProxyType, ProxyStatus,
    validate_proxy_config, parse_proxy_url, check_proxy_connectivity,
)


class ProxyHealthTests(unittest.TestCase):

    def test_proxy_config_url(self):
        c = ProxyConfig(ProxyType.HTTP, "proxy.example.com", 8080)
        self.assertEqual(c.url(), "http://proxy.example.com:8080")

    def test_proxy_config_url_with_auth(self):
        c = ProxyConfig(ProxyType.SOCKS5, "s.com", 1080, "user", "pass")
        self.assertEqual(c.url(), "socks5://user:pass@s.com:1080")

    def test_validate_empty_host(self):
        c = ProxyConfig(ProxyType.HTTP, "", 8080)
        issues = validate_proxy_config(c)
        self.assertTrue(any("host" in i.lower() for i in issues))

    def test_validate_invalid_port(self):
        c = ProxyConfig(ProxyType.HTTP, "host", 0)
        issues = validate_proxy_config(c)
        self.assertTrue(any("port" in i.lower() for i in issues))

    def test_validate_socks5_port_80(self):
        c = ProxyConfig(ProxyType.SOCKS5, "host", 80)
        issues = validate_proxy_config(c)
        self.assertTrue(any("unusual" in i.lower() for i in issues))

    def test_validate_good_config(self):
        c = ProxyConfig(ProxyType.HTTPS, "proxy.com", 443)
        self.assertEqual(validate_proxy_config(c), [])

    def test_parse_http_proxy(self):
        c = parse_proxy_url("http://proxy.local:3128")
        self.assertIsNotNone(c)
        self.assertEqual(c.proxy_type, ProxyType.HTTP)
        self.assertEqual(c.host, "proxy.local")
        self.assertEqual(c.port, 3128)

    def test_parse_socks5_proxy(self):
        c = parse_proxy_url("socks5://user:pw@socks.local:1080")
        self.assertIsNotNone(c)
        self.assertEqual(c.proxy_type, ProxyType.SOCKS5)
        self.assertEqual(c.username, "user")

    def test_parse_invalid_scheme(self):
        self.assertIsNone(parse_proxy_url("ftp://proxy:21"))

    def test_parse_empty(self):
        self.assertIsNone(parse_proxy_url(""))

    def test_connectivity_unreachable(self):
        # Connect to a port that's almost certainly not listening
        c = ProxyConfig(ProxyType.HTTP, "127.0.0.1", 19999)
        result = check_proxy_connectivity(c, timeout=1.0)
        self.assertIn(result.status, (ProxyStatus.UNREACHABLE, ProxyStatus.ERROR))


if __name__ == "__main__":
    unittest.main()
