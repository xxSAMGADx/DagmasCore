#!/usr/bin/env python3
"""
Unit tests for SpectorInspector (src/spector.py).
Tests injection snippet generation, optimal frame profiling, and bottleneck detection.
"""

import unittest
from src.spector import SpectorInspector

class TestSpector(unittest.TestCase):

    def setUp(self):
        self.spector = SpectorInspector(max_draw_calls=150)

    def test_injection_script_contains_spector_bundle(self):
        script = self.spector.generate_injection_script()
        self.assertIn("spector.bundle.js", script)
        self.assertIn("SPECTOR.Spector()", script)

    def test_optimal_frame_evaluation(self):
        report = self.spector.analyze_frame(
            draw_calls=50,
            fps=60.0,
            total_triangles=30000,
            shader_switches=10,
            textures_bound=8
        )
        self.assertEqual(report["status"], "OPTIMAL")
        self.assertTrue(report["within_budget"])

    def test_bottleneck_detection_high_draw_calls(self):
        report = self.spector.analyze_frame(
            draw_calls=350,  # Exceeds 150 budget
            fps=58.0,
            total_triangles=40000
        )
        self.assertEqual(report["status"], "BOTTLENECK")
        self.assertFalse(report["within_budget"])
        self.assertTrue(any("Draw call budget exceeded" in rec for rec in report["recommendations"]))

    def test_degraded_framerate_detection(self):
        report = self.spector.analyze_frame(
            draw_calls=80,
            fps=38.5,  # Below 55 FPS
            total_triangles=40000
        )
        self.assertEqual(report["status"], "DEGRADED")
        self.assertFalse(report["within_budget"])
        self.assertTrue(any("below 60 FPS target" in rec for rec in report["recommendations"]))


class TestADHDSkillSkeptor(unittest.TestCase):

    def setUp(self):
        from src.spector import ADHDSkillSkeptor
        self.skeptor = ADHDSkillSkeptor()

    def test_hyperfocus_locking_and_alignment(self):
        lock_res = self.skeptor.set_focus_goal("Implement Nostr agent encrypted envelope")
        self.assertEqual(lock_res["status"], "LOCKED")
        self.assertTrue(self.skeptor.locked)

        # Aligned action
        res = self.skeptor.audit_action("Writing tests for agent encrypted envelope")
        self.assertTrue(res["allowed"])
        self.assertEqual(res["status"], "ALIGNED")

    def test_distraction_detection_and_strike_counter(self):
        self.skeptor.set_focus_goal("Ship quantum graph database indexing")
        # Off-topic distraction
        distraction = self.skeptor.audit_action("Browsing unrelated Twitter memes and playing Tetris")
        self.assertFalse(distraction["allowed"])
        self.assertIn("Distraction detected", distraction["warning"])
        self.assertEqual(distraction["distraction_strikes"], 1)

    def test_goal_completion(self):
        self.skeptor.set_focus_goal("Build WebGPU shader pipeline")
        self.skeptor.audit_action("Browsing YouTube cats")
        res = self.skeptor.complete_goal()
        self.assertEqual(res["status"], "COMPLETED")
        self.assertFalse(self.skeptor.locked)
        self.assertEqual(res["distractions_blocked"], 1)

    def test_profile_graphics_integration(self):
        report = self.skeptor.profile_graphics_fps(draw_calls=45, fps=60.0, total_triangles=20000)
        self.assertEqual(report["status"], "OPTIMAL")
        self.assertTrue(report["within_budget"])


if __name__ == "__main__":
    unittest.main()

