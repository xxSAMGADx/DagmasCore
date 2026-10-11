#!/usr/bin/env python3
"""
Unit tests for BossReportEngine (src/boss_report.py).
Tests daily report generation, employee memory updating, and dynamic DOs/DONTs synchronization.
"""

import os
import unittest
import tempfile
from pathlib import Path
from src.boss_report import BossReportEngine
from src.teams import TeamHierarchyManager
from src.vault import VaultSandbox

class TestBossReport(unittest.TestCase):

    def test_boss_report_cycle(self):
        with tempfile.TemporaryDirectory() as td:
            vault = VaultSandbox(td)
            vault.initialize()

            # Provision default teams
            thm = TeamHierarchyManager(vault.teams_dir)
            thm.provision_default_teams()

            engine = BossReportEngine(td)
            result = engine.generate_daily_boss_report(date_str="2026-10-10")

            self.assertEqual(result["date"], "2026-10-10")
            self.assertGreater(result["evaluations_count"], 0)
            self.assertGreater(result["total_tasks"], 0)
            self.assertTrue(Path(result["report_file"]).exists())

            # Verify memory file creation
            mem_files = list(engine.employee_memory_dir.glob("*_memory.json"))
            self.assertGreater(len(mem_files), 0)

            # Verify SOUL update
            soul_files = list(vault.teams_dir.glob("*_SOUL.md"))
            self.assertGreater(len(soul_files), 0)
            sample_soul = soul_files[0].read_text()
            self.assertIn("### DO:", sample_soul)
            self.assertIn("### DONT:", sample_soul)

            # Verify living ledger updates
            do_content = (vault.ledgers_dir / "DO.md").read_text()
            dont_content = (vault.ledgers_dir / "DONT.md").read_text()
            self.assertIn("[Boss Review]", do_content)
            self.assertIn("[Boss Review]", dont_content)

if __name__ == "__main__":
    unittest.main()
