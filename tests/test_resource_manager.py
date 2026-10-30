"""Tests for AF-09: Resource Manager."""
import tempfile
import unittest
from pathlib import Path

from devseatech_browser.resource_manager import (
    ResourceKind, ResourcePolicy, ResourceSnapshot, Severity,
    check_policy, format_report, measure_memory,
    measure_profile_disk, measure_all_profiles_disk,
)


class ResourceSnapshotTests(unittest.TestCase):

    def test_snapshot_fields(self):
        s = ResourceSnapshot(ResourceKind.MEMORY, 1024.0, "test", 1.0)
        self.assertEqual(s.kind, ResourceKind.MEMORY)
        self.assertEqual(s.value, 1024.0)

    def test_measure_memory_returns_snapshot(self):
        snap = measure_memory()
        self.assertEqual(snap.kind, ResourceKind.MEMORY)
        self.assertGreaterEqual(snap.value, 0.0)
        self.assertGreater(snap.timestamp, 0.0)


class DiskMeasureTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.profile = Path(self.tmp) / "profile"
        self.profile.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_measure_empty_profile(self):
        snap = measure_profile_disk(self.profile)
        self.assertEqual(snap.kind, ResourceKind.DISK)
        self.assertEqual(snap.value, 0.0)

    def test_measure_profile_with_files(self):
        (self.profile / "data.txt").write_text("x" * 1000)
        snap = measure_profile_disk(self.profile)
        self.assertGreaterEqual(snap.value, 1000.0)

    def test_measure_missing_dir(self):
        snap = measure_profile_disk(Path("/nonexistent/path"))
        self.assertEqual(snap.value, 0.0)

    def test_measure_all_profiles(self):
        profiles = Path(self.tmp) / "profiles"
        profiles.mkdir()
        (profiles / "alpha").mkdir()
        (profiles / "alpha" / "f.txt").write_text("hello")
        (profiles / "beta").mkdir()
        snaps = measure_all_profiles_disk(profiles)
        self.assertEqual(len(snaps), 2)
        names = [s.label for s in snaps]
        self.assertTrue(any("alpha" in n for n in names))


class PolicyTests(unittest.TestCase):

    def test_no_violations(self):
        snaps = [ResourceSnapshot(ResourceKind.MEMORY, 100 * 1024 * 1024.0)]
        violations = check_policy(snaps)
        self.assertEqual(violations, [])

    def test_memory_warning(self):
        policy = ResourcePolicy(memory_warning_bytes=100)
        snaps = [ResourceSnapshot(ResourceKind.MEMORY, 200.0)]
        violations = check_policy(snaps, policy)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].severity, Severity.WARNING)

    def test_memory_critical(self):
        policy = ResourcePolicy(memory_critical_bytes=100)
        snaps = [ResourceSnapshot(ResourceKind.MEMORY, 200.0)]
        violations = check_policy(snaps, policy)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].severity, Severity.CRITICAL)

    def test_disk_warning(self):
        policy = ResourcePolicy(disk_warning_bytes=50)
        snaps = [ResourceSnapshot(ResourceKind.DISK, 100.0)]
        violations = check_policy(snaps, policy)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, ResourceKind.DISK)

    def test_cpu_warning(self):
        policy = ResourcePolicy(cpu_warning_pct=50.0)
        snaps = [ResourceSnapshot(ResourceKind.CPU, 75.0)]
        violations = check_policy(snaps, policy)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].kind, ResourceKind.CPU)

    def test_format_report_clean(self):
        snaps = [ResourceSnapshot(ResourceKind.MEMORY, 1024.0, "RSS: 0.0 MiB")]
        report = format_report(snaps, [])
        self.assertIn("All resources within limits", report)

    def test_format_report_violations(self):
        from devseatech_browser.resource_manager import PolicyViolation
        snaps = [ResourceSnapshot(ResourceKind.CPU, 99.0, "CPU high")]
        vs = [PolicyViolation(ResourceKind.CPU, Severity.CRITICAL,
                              99.0, 95.0, "CPU critical")]
        report = format_report(snaps, vs)
        self.assertIn("CRITICAL", report)


if __name__ == "__main__":
    unittest.main()
