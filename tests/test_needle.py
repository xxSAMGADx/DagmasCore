#!/usr/bin/env python3
"""
Unit tests for NeedleEngine (src/needle.py).
Tests routing decomposition, local execution preference, and tool validation.
"""

import unittest
from src.needle import NeedleEngine

class TestNeedleEngine(unittest.TestCase):

    def setUp(self):
        self.needle = NeedleEngine()

    def test_local_first_routing(self):
        res = self.needle.route_execution("Refactor auth module and run unit tests")
        self.assertEqual(res["route"], "NEEDLE_LOCAL_AUTOMATION")
        self.assertFalse(res["sanitization_required"])

    def test_cloud_escalation_trigger(self):
        res = self.needle.route_execution("Cross-repo multi-million token synthesis across 50 repos")
        self.assertEqual(res["route"], "CLOUD_ESCALATION")
        self.assertTrue(res["sanitization_required"])

    def test_plan_structure(self):
        plan = self.needle.plan("Implement unit tests for database module")
        self.assertTrue(plan["validated"])
        self.assertEqual(plan["planning_mode"], "rule_based_router")
        self.assertIsInstance(plan["steps"], list)
        self.assertGreater(len(plan["steps"]), 0)

    def test_tool_allowlist(self):
        self.assertTrue(self.needle.validate_tool("run_command"))
        self.assertTrue(self.needle.validate_tool("view_file"))
        self.assertFalse(self.needle.validate_tool("unauthorized_dangerous_tool"))

    def test_optional_skills_catalog(self):
        catalog = self.needle.get_optional_skills_catalog()
        self.assertIsInstance(catalog, dict)
        # Lean core default: no third-party bloat out of the box
        self.assertEqual(len(catalog), 0)

        # Dynamic registration of custom / community skills
        self.needle.register_optional_skill(
            skill_id="custom-domain-skill",
            name="Custom Domain Skill",
            url="https://github.com/example/custom-domain-skill",
            description="Specialized domain skill dynamically registered into Brain Vault."
        )
        updated_catalog = self.needle.get_optional_skills_catalog()
        self.assertIn("custom-domain-skill", updated_catalog)
        self.assertEqual(updated_catalog["custom-domain-skill"]["name"], "Custom Domain Skill")
        self.assertTrue(updated_catalog["custom-domain-skill"]["url"].startswith("http"))
        self.assertTrue(len(updated_catalog["custom-domain-skill"]["description"]) > 10)

    def test_cactus_needle_spec(self):
        spec = self.needle.get_cactus_needle_spec()
        self.assertIsInstance(spec, dict)
        self.assertEqual(spec["provider"], "Cactus Compute")
        self.assertEqual(spec["model_series"], "Needle 3")
        self.assertEqual(spec["repo"], "https://github.com/cactus-compute/needle")
        self.assertIn("tool_calling", spec["capabilities"])
        self.assertIn("structured_extraction", spec["capabilities"])
        self.assertIn("whistle_speech_to_text", spec["capabilities"])

    def test_cactus_needle_workflow_execution(self):
        # Local workflow execution with calibrated confidence
        wf = self.needle.run_cactus_workflow("Execute git commit and run unit tests")
        self.assertIn("Needle 3", wf["engine"])
        self.assertTrue(wf["calibrated"])
        self.assertGreaterEqual(wf["confidence"], 0.9)
        self.assertIsInstance(wf["function_calls"], list)

        # Cloud escalation workflow test
        cloud_wf = self.needle.run_cactus_workflow("Generate cloud video using external Sora API")
        self.assertLess(cloud_wf["confidence"], 0.5)

    def test_cactus_needle_available_check(self):
        is_avail = self.needle.check_cactus_needle_available()
        self.assertIsInstance(is_avail, bool)


if __name__ == "__main__":

    unittest.main()
