"""Subscription policy regression tests; no Qt dependency."""
import unittest

from devseatech_browser.subscription_policy import (
    SubscriptionStatus, expiry_policy, may_launch_browser,
)


class SubscriptionPolicyTests(unittest.TestCase):
    def test_expired_and_unverified_cannot_launch(self):
        for status in SubscriptionStatus:
            if status not in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING):
                self.assertFalse(may_launch_browser(status, server_verified=True))
            self.assertFalse(may_launch_browser(status, server_verified=False))

    def test_verified_active_or_trial_can_launch(self):
        self.assertTrue(may_launch_browser(SubscriptionStatus.ACTIVE, server_verified=True))
        self.assertTrue(may_launch_browser(SubscriptionStatus.TRIALING, server_verified=True))

    def test_expiry_never_deletes_profile_data(self):
        policy = expiry_policy()
        self.assertTrue(policy["preserve_local_profiles"])
        self.assertTrue(policy["preserve_cookies_cache_bookmarks"])
        self.assertFalse(policy["delete_local_data_on_expiry"])
        self.assertTrue(policy["block_browser_launch_until_renewal"])


if __name__ == "__main__":
    unittest.main()
