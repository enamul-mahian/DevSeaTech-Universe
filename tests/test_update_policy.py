"""Standard-library tests for default-off update eligibility."""
import unittest

from devseatech_browser.update_policy import (
    ReleaseCandidate,
    UpdatePolicy,
    eligible_for_automatic_install,
)


class UpdatePolicyTests(unittest.TestCase):
    def setUp(self):
        self.valid = ReleaseCandidate(
            published=True, approved=True,
            signature_verified=True, compatible=True
        )

    def test_default_is_off(self):
        self.assertFalse(UpdatePolicy().auto_update_enabled)
        self.assertFalse(eligible_for_automatic_install(UpdatePolicy(), self.valid))

    def test_explicit_opt_in_with_valid_release(self):
        self.assertTrue(
            eligible_for_automatic_install(UpdatePolicy(True), self.valid)
        )

    def test_unpublished_commit_is_not_a_release(self):
        candidate = ReleaseCandidate(False, True, True, True)
        self.assertFalse(
            eligible_for_automatic_install(UpdatePolicy(True), candidate)
        )

    def test_unapproved_release_is_rejected(self):
        self.assertFalse(eligible_for_automatic_install(
            UpdatePolicy(True), ReleaseCandidate(True, False, True, True)
        ))

    def test_unsigned_incompatible_or_downgrade_rejected(self):
        for candidate in (
            ReleaseCandidate(True, True, False, True),
            ReleaseCandidate(True, True, True, False),
            ReleaseCandidate(True, True, True, True, downgrade=True),
        ):
            with self.subTest(candidate=candidate):
                self.assertFalse(eligible_for_automatic_install(
                    UpdatePolicy(True), candidate
                ))


if __name__ == "__main__":
    unittest.main()
