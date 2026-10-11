import unittest
import tempfile
import shutil
import os
import stat
from pathlib import Path

from src.preflight import PreflightEngine
from src.vault import VaultSandbox

class TestPreflightEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_preflight_vault_")
        self.vault = VaultSandbox(self.temp_dir)
        self.vault.initialize()
        self.engine = PreflightEngine(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_preflight_on_initialized_vault(self):
        report = self.engine.run_all(auto_fix=True)
        self.assertIn("overall_status", report)
        self.assertIn("checks", report)
        self.assertIn("fixes_applied", report)
        self.assertIn(report["overall_status"], ["PASS", "WARN"])
        self.assertEqual(report["exit_code"], 0)

    def test_preflight_self_healing_permissions(self):
        # Degrade permissions to 0755
        os.chmod(self.temp_dir, 0o755)
        current_mode = os.stat(self.temp_dir).st_mode & 0o777
        self.assertEqual(current_mode, 0o755)

        # Run preflight with auto_fix
        report = self.engine.run_all(auto_fix=True)
        repaired_mode = os.stat(self.temp_dir).st_mode & 0o777
        self.assertEqual(repaired_mode, 0o700)
        self.assertTrue(any("Fixed vault permissions" in f for f in report["fixes_applied"]))

    def test_preflight_self_healing_missing_ledgers(self):
        do_file = Path(self.temp_dir) / "ledgers" / "DO.md"
        if do_file.exists():
            do_file.unlink()
        self.assertFalse(do_file.exists())

        report = self.engine.run_all(auto_fix=True)
        self.assertTrue(do_file.exists())
        self.assertTrue(any("DO.md" in f for f in report["fixes_applied"]))

    def test_preflight_diagnostic_reporting_structure(self):
        report = self.engine.run_all(auto_fix=False)
        check_names = [c["name"] for c in report["checks"]]
        self.assertIn("sandbox_integrity", check_names)
        self.assertIn("config_and_keystore", check_names)
        self.assertIn("local_reasoning_engines", check_names)
        self.assertIn("qdrant_vector_db", check_names)
        self.assertIn("regression_tests", check_names)

if __name__ == "__main__":
    unittest.main()
