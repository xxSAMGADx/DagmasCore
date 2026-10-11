#!/usr/bin/env python3
"""
Unit tests for SkillInstaller (src/installer.py).
Tests:
1. Environment detection across platforms.
2. Skill copying into custom target directory.
3. Global agent rule generation and file permissions.
4. Claude Desktop MCP server configuration injection.
5. Safe uninstallation of skill and rules.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from src.installer import SkillInstaller

class TestSkillInstaller(unittest.TestCase):

    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.td.name)
        self.installer = SkillInstaller()

    def tearDown(self):
        self.td.cleanup()

    def test_detect_environment(self):
        env = self.installer.detect_environment()
        self.assertIn("platform", env)
        self.assertIn("python_executable", env)
        self.assertIn("default_skill_dest", env)
        self.assertIn("default_rule_dest", env)

    def test_install_skill_to_custom_directory(self):
        dest = self.temp_path / "custom_skills" / "brain-vault-setup"
        res = self.installer.install_skill(dest_dir=dest)
        self.assertTrue(res["success"])
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "SKILL.md").exists())
        self.assertIn("SKILL.md", res["files_copied"])

    def test_install_global_rule(self):
        rule_dest = self.temp_path / "rules" / "dagmas_brain_vault.md"
        res = self.installer.install_global_rule(dest_file=rule_dest)
        self.assertTrue(res["success"])
        self.assertTrue(rule_dest.exists())
        content = rule_dest.read_text(encoding="utf-8")
        self.assertIn("# DAGMAS Brain Vault Global Agent Standards", content)
        self.assertIn("0700", content)
        self.assertNotIn("buzz", content.lower())
        self.assertNotIn("hermes", content.lower())

    def test_configure_claude_desktop_mcp(self):
        cfg_dest = self.temp_path / "claude_desktop_config.json"
        # Pre-seed existing config
        cfg_dest.write_text(json.dumps({"mcpServers": {"existing-tool": {"command": "node"}}}), encoding="utf-8")

        res = self.installer.configure_claude_desktop(config_path=cfg_dest)
        self.assertTrue(res["success"])

        updated = json.loads(cfg_dest.read_text(encoding="utf-8"))
        self.assertIn("brain-vault", updated["mcpServers"])
        self.assertIn("existing-tool", updated["mcpServers"])
        self.assertEqual(updated["mcpServers"]["brain-vault"]["args"], ["-m", "src.mcp_server"])

    def test_uninstall(self):
        dest = self.temp_path / "to_delete_skill"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("dummy", encoding="utf-8")

        rule_dest = self.temp_path / "to_delete_rule.md"
        rule_dest.write_text("dummy rule", encoding="utf-8")

        un_res = self.installer.uninstall(skill_dir=dest, rule_file=rule_dest)
        self.assertTrue(un_res["success"])
        self.assertFalse(dest.exists())
        self.assertFalse(rule_dest.exists())

if __name__ == "__main__":
    unittest.main()
